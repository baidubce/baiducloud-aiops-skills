---
name: baiducloud-openclaw-apm-monitoring
description: Configure and verify OpenClaw telemetry export to Baidu Cloud BCM APM through the official diagnostics-otel plugin. Use when connecting an installed OpenClaw Gateway with an endpoint and complete auth value, enabling model and tool content capture, or troubleshooting native trace export.
---

# OpenClaw APM Monitoring

## Overview

Connect an installed, working OpenClaw Gateway to Baidu Cloud BCM LLM application monitoring through the official `@openclaw/diagnostics-otel` plugin. Export native traces, model messages, tool content, and token usage over HTTP/protobuf. The default application name is `openclaw`. The validated baseline is **OpenClaw 2026.9.3** with the matching official plugin.

## Required Inputs

| User input | Configuration |
| --- | --- |
| `endpoint` | Append `/api/public/otel/v1/traces` to an origin URL. Treat a URL that already contains a path as the complete ingestion URL. Write the result to `diagnostics.otel.tracesEndpoint`. |
| `auth` | Write the **complete Authorization value** supplied by the console or receiver to `diagnostics.otel.headers.Authorization`, unchanged. |

Reuse values already supplied and ask only for a missing value. Default the application name to `openclaw`; override it only when the user requests another name. Do not require an application name, session ID, user ID, Langfuse public/secret keys, AK/SK, or Gateway token as additional onboarding inputs.

Use the endpoint and auth for the same account and target region from the [BCM LLM application monitoring access page](https://console.bce.baidu.com/bcm/#/bcm/llm/apmApplication/access-doc). Send telemetry only to the receiver chosen by the user.

This skill uses the validated **BCM LLM/Langfuse-compatible trace ingestion route**. Do not copy the OpenCode example's `Authentication` header or Hermes' Langfuse environment variables into this setup. Do not add a `Basic` or `Bearer` prefix, Base64-encode auth, or append a placeholder secret. If a receiver provides a bare token and requires a different header, establish that receiver's actual contract before adapting the configuration.

## Configuration Written to OpenClaw

The configuration is built by `buildPatch()` in [scripts/configure.mjs](scripts/configure.mjs) and merged into the active OpenClaw configuration using `openclaw config patch --stdin`. The usual file is `~/.openclaw/openclaw.json`; profiles and environment overrides can change it. Resolve the actual file on the Gateway host with:

```bash
openclaw config file --json
```

| Configuration key | Value | Purpose |
| --- | --- | --- |
| `plugins.entries.diagnostics-otel.enabled` | `true` | Enable the official exporter plugin. |
| `diagnostics.enabled` | `true` | Enable runtime diagnostic events. |
| `diagnostics.otel.enabled` | `true` | Enable OpenTelemetry export. |
| `diagnostics.otel.tracesEndpoint` | Normalized user endpoint | Set the complete trace ingestion URL. |
| `diagnostics.otel.headers.Authorization` | Complete user auth | Authenticate export requests. |
| `diagnostics.otel.protocol` | `http/protobuf` | Export OTLP protobuf over HTTP. |
| `diagnostics.otel.serviceName` | `openclaw` | Set the APM application name. |
| `diagnostics.otel.captureContent` | `true` | Capture bounded, redacted model messages and tool arguments/results. |
| `diagnostics.otel.traces` | `true` | Export traces. |
| `diagnostics.otel.sampleRate` | `1` | Sample all root traces during onboarding. |
| `diagnostics.otel.metrics` / `diagnostics.otel.logs` | `false` | Disable the plugin's extra metric and log signals; token attributes remain in traces. |

For message/context content, the switch is **`diagnostics.otel.captureContent`**. It belongs under `diagnostics.otel`, not under the plugin's own `config`. It does not enable unrestricted system-prompt or internal-reasoning export. The complete JSON merge example and field details are in [Configuration File and Default Settings](references/openclaw-otel.md#configuration-file-and-default-settings).

## Workflow

### 1. Inspect the Instance and Version

Run on the **host or container where the Gateway actually runs**, using its account, profile, `OPENCLAW_CONFIG_PATH`, and `OPENCLAW_STATE_DIR`. A separate configuration inside a tool sandbox does not configure the host Gateway.

```bash
openclaw --version
node --version
openclaw config file --json
```

- For **2026.9.3 or a newer stable release**, match the official plugin to the exact installed core version. Do not install an unversioned `latest` plugin.
- For an older release, incompatible Node runtime, declarative installation, or plugin installation failure, read [Versions and Managed Installations](references/openclaw-otel.md#versions-and-managed-installations). Do not silently downgrade a newer installation or pair a new plugin with an old core.
- Configure the existing installation without creating model accounts or changing models, channels, or search settings.

Briefly tell the user that setup enables model/tool content capture, creates a private configuration backup, and requires a Gateway restart. An explicit request to connect APM authorizes this setup; continue unless actual host permissions or credentials are missing.

### 2. Run the Configuration Script

The script uses the official JSON5-aware configuration CLI to validate and merge changes. It:

1. Backs up the active configuration in a directory with mode `0700`, with backup file mode `0600`.
2. Installs or updates only the matching official `diagnostics-otel` plugin when needed.
3. Enables it, appends it to an existing allowlist, and removes only its own deny entry.
4. Disables an existing `langfuse-bridge` to prevent duplicate export.
5. Applies the settings listed above while preserving unrelated configuration.
6. Replaces telemetry headers with the supplied `Authorization` so credentials for an old receiver are not sent to a new endpoint.

**Do not pass auth as a command-line argument.** Use an existing private file or pass it as data through the execution tool's stdin. If the user supplies only auth text, create a temporary file with mode `0600` in the Gateway account's private directory and write the value through a file-writing tool. The user does not need to prepare a third input. Keep auth out of the skill, reports, terminal output, and shareable commands. The script persists it in the restricted active configuration, so the daemon does not depend on a temporary shell variable.

With a private auth file:

```bash
node "{baseDir}/scripts/configure.mjs" \
  --endpoint '<user-endpoint>' \
  --auth-file '<private-auth-file-path>' \
  --no-restart
```

Alternatively, use `--auth-stdin` and provide the complete auth through the execution tool's stdin. If `OPENCLAW_APM_AUTHORIZATION` is already set, omit the auth input options. Never interpolate a token into shell command text. Delete a temporary auth file created for this operation after success; retain the user's existing credential files.

Optional execution flags: `--dry-run` prints a redacted plan and validates the schema when the plugin is already installed; `--service-name` overrides the application name; `--cli` selects the actual OpenClaw executable or `openclaw.mjs` entry. These are execution options, not extra required user inputs.

If the user explicitly requests metadata only, use the reference's manual merge with `captureContent=false` instead of the default script. Do not require message I/O during metadata-only verification.

### 3. Restart and Check

Inside an OpenClaw session, prefer the available Gateway restart tool so the Gateway manages its own restart. Resume checks after reconnection; a restart-induced session interruption is not itself a configuration failure.

From an external host terminal:

```bash
openclaw gateway restart
node "{baseDir}/scripts/configure.mjs" --check
```

When the configuration script runs in an independent host process, `--restart` can perform both the restart and local checks. For Docker, systemd, launchd, or a foreground Gateway, use the installation's existing service lifecycle. Do not start a second Gateway. Confirm that the service also uses a supported Node runtime.

`localConfigReady=true` means that configuration, plugin loading, and Gateway health checks passed. **It does not prove that APM received the traces.**

### 4. Generate a Real Native Request

```bash
node "{baseDir}/scripts/verify.mjs"
```

The script selects the default configured agent and invokes `gateway call chat.send` with a unique marker and `deliver=false`, so it does not send a message to an external channel. It polls `chat.history` for completion and prints only timestamps, the marker, run ID, and local usage. It does not print conversation content or internal reasoning.

This makes one real model request using the existing account. Do not substitute handwritten spans, an empty JSON POST, Langfuse `auth_check()`, or an endpoint-root GET for native request verification. After a timeout, inspect the original request before submitting another.

### 5. Verify Ingestion and Report

When an APM console or query interface is available, find the raw spans by application name `openclaw`, test time, and marker. Verify:

- `openclaw.model.call` contains the model name, raw input/output messages, actual duration, and provider-reported token usage.
- Each nonempty parent span ID resolves within the same trace.
- `openclaw.model.usage` is a run summary and is not added again to the individual `model.call` usage.

If tool verification is needed, make a separate harmless tool request with a unique marker, such as a single `printf`. Inspect tool arguments/results and the model message `tool_call` / `tool_call_response` parts. See [Ingestion Verification and Known Limits](references/openclaw-otel.md#ingestion-verification-and-known-limits) for details.

With only endpoint/auth and no query access, still complete configuration, restart, and the real request test. Report that local checks passed and the native request completed, while APM receipt remains unverified; include the marker and timestamps. Do not require another cloud account as an onboarding prerequisite or claim complete end-to-end verification without receiver evidence.

Report the actual core/plugin versions, application name, configuration and backup paths, restart status, local checks, and APM receipt status. Always hide auth. Do not repeatedly change correct native collection settings to work around server-side classification or display issues.

## References

- [OpenClaw OTel Configuration and Troubleshooting](references/openclaw-otel.md): full JSON settings, upgrades, rollback, 401/404 errors, missing I/O, duplicate tokens, and Gateway restart issues.
- [RAM Policies](references/ram-policies.md): receiver auth grants ingestion access; setup does not require additional cloud resource administration permissions.
