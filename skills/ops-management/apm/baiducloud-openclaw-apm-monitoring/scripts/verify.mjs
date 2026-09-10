#!/usr/bin/env node
// Generate one real, non-delivered Gateway model request through native OTel.
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { parseArgs } from 'node:util';
import { pathToFileURL } from 'node:url';
import { setTimeout as sleep } from 'node:timers/promises';
import { createCLI, parseJSONOutput, checkLocal } from './configure.mjs';

function visibleText(message) {
  if (typeof message.content === 'string') return message.content;
  return (Array.isArray(message.content) ? message.content : [])
    .filter(part => part?.type === 'text').map(part => part.text || '').join('\n');
}

export async function main(argv = process.argv.slice(2)) {
  const { values: opts } = parseArgs({ args: argv, options: {
    cli: { type: 'string', default: 'openclaw' }, agent: { type: 'string' },
    'timeout-seconds': { type: 'string', default: '150' }, help: { type: 'boolean' },
  } });
  if (opts.help) {
    console.log('node verify.mjs [--agent ID] [--timeout-seconds 150] [--cli PATH]\nSends one real model request with deliver=false. Does not prove APM ingestion.');
    return;
  }
  const seconds = Number(opts['timeout-seconds']);
  if (!Number.isFinite(seconds) || seconds < 10 || seconds > 600) throw new Error('timeout-seconds must be between 10 and 600.');
  const cli = createCLI(opts.cli);
  const report = checkLocal(cli);
  if (!report.localConfigReady) throw new Error(`Local checks failed: ${report.issues.join(', ')}. Complete configuration and restart first.`);
  const agents = parseJSONOutput(cli(['agents', 'list', '--json']));
  if (!Array.isArray(agents)) throw new Error('Could not read the configured agents.');
  const agent = opts.agent ? agents.find(a => a.id === opts.agent) : agents.find(a => a.isDefault) || agents[0];
  if (!agent?.id) throw new Error('No configured agent is available; this skill does not create model accounts.');
  const suffix = randomUUID().replaceAll('-', '');
  const marker = `APM_OPENCLAW_${suffix}`;
  const sessionKey = `agent:${agent.id}:apm-check-${suffix}`;
  const rpc = (method, params) => parseJSONOutput(cli([
    'gateway', 'call', method, '--json', '--timeout', '15000', '--params', JSON.stringify(params),
  ], { timeout: 20000 }));
  const startedAt = new Date().toISOString();
  const receipt = rpc('chat.send', {
    sessionKey, message: `This is a nonsensitive monitoring setup check. Do not use tools. Reply only with ${marker}.`,
    thinking: 'minimal', deliver: false, idempotencyKey: `apm-check-${suffix}`,
  });
  console.log(JSON.stringify({ stage: 'request_submitted', marker, runId: receipt.runId, startedAt }));
  const deadline = Date.now() + seconds * 1000;
  while (Date.now() < deadline) {
    const history = rpc('chat.history', { sessionKey, limit: 20 });
    const messages = Array.isArray(history.messages) ? history.messages : [];
    const replies = messages.filter(m => m.role === 'assistant' && visibleText(m).includes(marker));
    const info = history.sessionInfo || {};
    if (replies.length && !info.hasActiveRun &&
        (info.status === 'done' || info.status == null || ['stop', 'end_turn'].includes(replies.at(-1).stopReason))) {
      const usage = replies.at(-1).usage || {};
      const localUsage = {};
      for (const key of ['input', 'output', 'cacheRead', 'cacheWrite', 'totalTokens']) {
        if (typeof usage[key] === 'number') localUsage[key] = usage[key];
      }
      console.log(JSON.stringify({
        stage: 'native_request_completed', marker, runId: receipt.runId,
        serviceName: report.serviceName, startedAt, completedAt: new Date().toISOString(),
        localUsage, apmReceiptVerified: false,
        nextCheck: 'Find native openclaw.model.call spans in APM using the application name, test time, and marker.',
      }, null, 2));
      return;
    }
    await sleep(2000);
  }
  throw new Error(`The test request did not complete within the time limit. Look up marker=${marker} before submitting another request.`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  main().catch(error => { console.error(error.message); process.exitCode = 1; });
}
