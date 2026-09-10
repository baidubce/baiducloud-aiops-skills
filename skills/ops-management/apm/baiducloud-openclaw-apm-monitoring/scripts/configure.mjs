#!/usr/bin/env node
// Configure the official OpenClaw exporter. No SDK, bridge, or source patches.
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { parseArgs } from 'node:util';
import { pathToFileURL } from 'node:url';

export const BASELINE = '2026.9.3';
const PLUGIN = 'diagnostics-otel';

export function normalizeEndpoint(value) {
  const endpoint = value.trim();
  if (/[\x00-\x20\x7f]/.test(endpoint)) throw new Error('endpoint must not contain whitespace or control characters.');
  let url;
  try { url = new URL(endpoint); } catch { throw new Error('endpoint must be a complete HTTP or HTTPS URL.'); }
  if (!['http:', 'https:'].includes(url.protocol) || !url.hostname ||
      url.username || url.password || url.search || url.hash) {
    throw new Error('endpoint must use HTTP/HTTPS without embedded credentials, query parameters, or a fragment.');
  }
  // A console base/origin uses the previously verified BCM LLM ingestion path.
  // A URL with a path is already a complete write URL and is never guessed.
  return url.pathname === '/' ? `${url.origin}/api/public/otel/v1/traces` : endpoint;
}

export function validateAuth(value) {
  const auth = value.replace(/[\r\n]+$/, '');
  if (!auth || auth.length > 16384 || auth !== auth.trim() || /[\x00-\x1f\x7f]/.test(auth)) {
    throw new Error('auth must be a nonempty, single-line complete Authorization value without the header name or extra whitespace.');
  }
  return auth;
}

export function parseJSONOutput(text) {
  for (let i = 0; i < text.length; i++) {
    if (text[i] !== '{' && text[i] !== '[') continue;
    try { return JSON.parse(text.slice(i)); } catch { /* skip banners */ }
  }
  throw new Error('OpenClaw did not return recognizable JSON; check the CLI version and runtime logs.');
}

export function buildPatch(plugins, inventory, endpoint, auth, serviceName) {
  if (plugins.enabled === false) throw new Error('Plugins are globally disabled; check this installation\'s plugin management policy first.');
  if (plugins.allow !== undefined && !Array.isArray(plugins.allow)) throw new Error('plugins.allow must be an array.');
  if (plugins.deny !== undefined && !Array.isArray(plugins.deny)) throw new Error('plugins.deny must be an array.');
  const entries = { [PLUGIN]: { enabled: true } };
  if (plugins.entries?.['langfuse-bridge'] || inventory.some(p => p.id === 'langfuse-bridge')) {
    entries['langfuse-bridge'] = { enabled: false };
  }
  const pluginPatch = { entries };
  if (plugins.allow !== undefined) pluginPatch.allow = [...new Set([...plugins.allow, PLUGIN])];
  if (plugins.deny?.includes(PLUGIN)) pluginPatch.deny = plugins.deny.filter(id => id !== PLUGIN);
  return {
    plugins: pluginPatch,
    diagnostics: {
      enabled: true,
      otel: {
        enabled: true, tracesEndpoint: endpoint, protocol: 'http/protobuf',
        headers: { Authorization: auth }, serviceName,
        traces: true, metrics: false, logs: false, sampleRate: 1, captureContent: true,
      },
    },
  };
}

export function createCLI(binary = 'openclaw') {
  // An explicit .mjs entry also works on Windows without shell command parsing.
  const isModule = binary.endsWith('.mjs');
  const executable = isModule ? process.execPath : binary;
  const prefix = isModule ? [binary] : [];
  return function cli(args, { input = '', timeout = 60000, optional = false } = {}) {
    const result = spawnSync(executable, [...prefix, ...args], {
      input, encoding: 'utf8', timeout, maxBuffer: 16 * 1024 * 1024,
      windowsHide: true, shell: false,
    });
    if (optional && result.status === 1) {
      const body = parseJSONOutput(result.stdout || '');
      if (/valid but unset|Config path not found/i.test(body?.error?.message || '')) return undefined;
    }
    if (result.error || result.status !== 0) {
      // Raw CLI output may contain other existing credentials; never echo it.
      throw new Error(`openclaw ${args.slice(0, 2).join(' ')} failed (${result.error?.code || result.status}); inspect redacted logs for that command.`);
    }
    return result.stdout;
  };
}

function getJSON(cli, args, options) {
  const text = cli(args, options);
  return text === undefined ? undefined : parseJSONOutput(text);
}

function readVersion(cli) {
  const version = cli(['--version']).match(/\b(\d{4}\.\d+\.\d+(?:-[\w.-]+)?)/)?.[1];
  if (!version) throw new Error('Could not identify the OpenClaw version.');
  const parts = version.split('.').map(Number);
  if (version.includes('-') || parts[0] < 2026 ||
      (parts[0] === 2026 && (parts[1] < 9 || (parts[1] === 9 && parts[2] < 3)))) {
    throw new Error(`OpenClaw ${version} is outside this skill's native integration baseline. Follow references/openclaw-otel.md to back up and upgrade to ${BASELINE} or a newer stable release.`);
  }
  return version;
}

function runtimeCheck() {
  const [major, minor] = process.versions.node.split('.').map(Number);
  if (!((major === 24 && minor >= 16) || (major === 26 && minor >= 1) || major > 26)) {
    throw new Error('Use Node 24.16.0+ (24.x) or 26.1.0+; Node 26 is recommended. The Gateway service must also use a supported Node runtime.');
  }
}

function inventoryOf(cli) {
  const data = getJSON(cli, ['plugins', 'list', '--json']);
  if (!Array.isArray(data.plugins)) throw new Error('Could not read the plugin inventory.');
  return data.plugins;
}

export function checkLocal(cli) {
  const version = readVersion(cli);
  cli(['config', 'validate', '--json']);
  const diagnostics = getJSON(cli, ['config', 'get', 'diagnostics', '--json'], { optional: true }) || {};
  const inventory = inventoryOf(cli);
  const plugin = inventory.find(p => p.id === PLUGIN);
  const bridge = inventory.find(p => p.id === 'langfuse-bridge');
  const otel = diagnostics.otel || {};
  const issues = [];
  if (!diagnostics.enabled || !otel.enabled || !otel.traces) issues.push('traces_not_enabled');
  if (otel.protocol !== 'http/protobuf') issues.push('protocol_mismatch');
  if (!otel.tracesEndpoint) issues.push('traces_endpoint_missing');
  if (!otel.headers?.Authorization) issues.push('authorization_missing');
  if (!otel.captureContent) issues.push('content_capture_disabled');
  if (otel.sampleRate === 0) issues.push('root_trace_sampling_disabled');
  if (otel.metrics !== false || otel.logs !== false) issues.push('extra_signals_enabled');
  if (!plugin?.enabled || plugin.status !== 'loaded') issues.push('native_plugin_not_loaded');
  if (plugin?.version !== version) issues.push('plugin_version_mismatch');
  if (bridge?.enabled) issues.push('bridge_still_enabled');
  if (process.env.OTEL_TRACES_EXPORTER?.split(',').map(x => x.trim()).includes('none')) issues.push('cli_environment_disables_trace_export');
  let gatewayReachable = false;
  try { cli(['health', '--json', '--timeout', '10000'], { timeout: 15000 }); gatewayReachable = true; }
  catch { issues.push('gateway_health_failed'); }
  let displayEndpoint;
  try {
    const url = new URL(otel.tracesEndpoint);
    displayEndpoint = `${url.protocol}//${url.host}${url.pathname}`;
  } catch { displayEndpoint = otel.tracesEndpoint ? '<invalid-or-unresolved-url>' : undefined; }
  return {
    openclawVersion: version,
    localConfigReady: issues.length === 0, issues, gatewayReachable,
    plugin: { id: PLUGIN, version: plugin?.version, status: plugin?.status },
    serviceName: otel.serviceName, tracesEndpoint: displayEndpoint,
    authorizationPresent: Boolean(otel.headers?.Authorization),
    apmReceiptVerified: false,
  };
}

export function main(argv = process.argv.slice(2)) {
  const { values: opts } = parseArgs({ args: argv, options: {
    endpoint: { type: 'string' }, 'auth-file': { type: 'string' }, 'auth-stdin': { type: 'boolean' },
    'service-name': { type: 'string', default: 'openclaw' }, cli: { type: 'string', default: 'openclaw' },
    'dry-run': { type: 'boolean' }, restart: { type: 'boolean' }, 'no-restart': { type: 'boolean' },
    check: { type: 'boolean' }, help: { type: 'boolean' },
  } });
  if (opts.help) {
    console.log('node configure.mjs --endpoint URL (--auth-file FILE | --auth-stdin) [--dry-run] [--restart]\nnode configure.mjs --check\nAuth also accepts OPENCLAW_APM_AUTHORIZATION. Default: configure only; restart the Gateway separately.');
    return;
  }
  if (opts.restart && opts['no-restart']) throw new Error('--restart and --no-restart cannot be used together.');
  runtimeCheck();
  const cli = createCLI(opts.cli);
  const version = readVersion(cli);
  if (opts.check) {
    const report = { openclawVersion: version, ...checkLocal(cli) };
    console.log(JSON.stringify(report, null, 2));
    if (!report.localConfigReady) process.exitCode = 2;
    return;
  }
  if (!opts.endpoint) throw new Error('Missing endpoint.');
  if (opts['auth-file'] && opts['auth-stdin']) throw new Error('Choose only one auth input method.');
  if (!opts['service-name'].trim() || opts['service-name'].length > 128 || /[\x00-\x1f]/.test(opts['service-name'])) throw new Error('The application name must be a single line containing 1 to 128 characters.');
  const endpoint = normalizeEndpoint(opts.endpoint);
  const rawAuth = opts['auth-file'] ? fs.readFileSync(opts['auth-file'], 'utf8') :
    opts['auth-stdin'] ? fs.readFileSync(0, 'utf8') : process.env.OPENCLAW_APM_AUTHORIZATION || '';
  const auth = validateAuth(rawAuth);
  cli(['config', 'validate', '--json']);
  const gatewayMode = getJSON(cli, ['config', 'get', 'gateway', '--json'], { optional: true })?.mode;
  if (gatewayMode === 'remote') throw new Error('This configuration belongs to a remote Gateway client; run setup on the actual Gateway host or container.');
  let plugins = getJSON(cli, ['config', 'get', 'plugins', '--json'], { optional: true }) || {};
  let inventory = inventoryOf(cli);
  const native = inventory.find(p => p.id === PLUGIN);
  const needsInstall = !native || native.version !== version;
  // Validate global policy and list shapes before any mutation.
  buildPatch(plugins, inventory, endpoint, auth, opts['service-name']);
  const plan = {
    openclawVersion: version, validatedBaseline: BASELINE,
    pluginPackage: `npm:@openclaw/diagnostics-otel@${version}`, installRequired: needsInstall,
    tracesEndpoint: endpoint, authorization: '<redacted>', serviceName: opts['service-name'],
    protocol: 'http/protobuf', captureContent: true, traces: true, metrics: false, logs: false,
    disableBridge: Boolean(plugins.entries?.['langfuse-bridge'] || inventory.some(p => p.id === 'langfuse-bridge')),
    restartRequested: Boolean(opts.restart), apmReceiptVerified: false,
  };
  if (opts['dry-run']) {
    if (!needsInstall) {
      cli(['config', 'patch', '--stdin', '--replace-path', 'diagnostics.otel.headers', '--dry-run', '--json'], {
        input: JSON.stringify(buildPatch(plugins, inventory, endpoint, auth, opts['service-name'])),
      });
    }
    console.log(JSON.stringify({ ...plan, dryRun: true, schemaValidated: !needsInstall }, null, 2));
    return;
  }

  if (process.env.OPENCLAW_NIX_MODE === '1') throw new Error('This installation uses read-only Nix configuration; merge the same fields through its declarative configuration workflow.');

  const file = getJSON(cli, ['config', 'file', '--json'])?.path;
  if (!file || !path.isAbsolute(file)) throw new Error('Could not resolve the active instance\'s configuration path.');
  if (!fs.lstatSync(file).isFile()) throw new Error('The active configuration is not a regular file; check this installation\'s configuration management method first.');
  const backupDir = fs.mkdtempSync(path.join(path.dirname(file), 'apm-config-backup-'));
  fs.chmodSync(backupDir, 0o700);
  const backup = path.join(backupDir, 'openclaw.json');
  fs.copyFileSync(file, backup, fs.constants.COPYFILE_EXCL);
  fs.chmodSync(backup, 0o600);
  console.log(JSON.stringify({ stage: 'backup_created', backup, includesSecrets: true }));
  if (needsInstall) {
    cli(['plugins', 'install', plan.pluginPackage, '--pin', '--force', '--accept-capabilities'], { timeout: 600000 });
    inventory = inventoryOf(cli);
    if (inventory.find(p => p.id === PLUGIN)?.version !== version) throw new Error('The plugin version still does not match after installation; retain the backup and inspect the installation result.');
    plugins = getJSON(cli, ['config', 'get', 'plugins', '--json'], { optional: true }) || {};
  }
  const patch = buildPatch(plugins, inventory, endpoint, auth, opts['service-name']);
  const patchArgs = ['config', 'patch', '--stdin', '--replace-path', 'diagnostics.otel.headers'];
  cli([...patchArgs, '--dry-run', '--json'], { input: JSON.stringify(patch) });
  cli(patchArgs, { input: JSON.stringify(patch) });
  fs.chmodSync(file, 0o600);
  cli(['config', 'validate', '--json']);
  console.log(JSON.stringify({ ...plan, stage: 'configured', backup, restartRequired: true }, null, 2));
  if (opts.restart) {
    cli(['gateway', 'restart'], { timeout: 120000 });
    const report = checkLocal(cli);
    console.log(JSON.stringify({ stage: 'post_restart_check', ...report }, null, 2));
    if (!report.localConfigReady) process.exitCode = 2;
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try { main(); }
  catch (error) { console.error(error.message); process.exitCode = 1; }
}
