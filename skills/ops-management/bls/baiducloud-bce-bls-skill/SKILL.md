---
name: baiducloud-bce-bls-skill
description: Install and verify the official Baidu Cloud Log Service (BLS) AI Agent skill (`bce-bls`) from the BLS documentation or packaged zip. Use when the user asks to install, update, download, configure, or troubleshoot the BLS installer skill, `bce-bls-skill` or legacy `bls-skill`, `bce-bls.zip`, OpenCode/OpenClaw skill installation, or natural-language querying of Baidu Cloud Log Service through an AI agent.
---

# BCE BLS Skill Installer

Use this skill to install the official Baidu Cloud Log Service (BLS) AI Agent skill into an agent's `skills` directory. The installed runtime skill is named `bce-bls`; this `bce-bls-skill` is only the installer and verification guide. Prefer the bundled `assets/bce-bls.zip` package so installation does not depend on reaching Baidu-hosted download URLs.

Official references:

- BLS AI Agent guide: https://cloud.baidu.com/doc/BLS/s/Omnr306y5
- BLS skill zip: https://bls-skill.bj.bcebos.com/latest/bce-bls.zip
- Bundled package: `assets/bce-bls.zip`

## Workflow

### 1. Pick The Target Skills Directory

Infer the target from the agent the user is using:

```text
OpenCode: ~/.config/opencode/skills
OpenClaw: {openclaw_path}/skills
Hermes: ~/.hermes/skills
Codex: ~/.codex/skills or $CODEX_HOME/skills
Other agents: the agent's documented skills directory
```

If the target cannot be inferred, ask for it. Do not install into the current repository unless the user explicitly wants a repository copy.

### 2. Prefer Native Package Installation When Available

For OpenClaw, the official document says users can install this installer skill directly with:

```bash
openclaw skills install bce-bls-skill
```

For portable installs, use the bundled installer script. It installs from `assets/bce-bls.zip` when present and only falls back to the official URL if the bundled package is missing:

```bash
bash scripts/install-bce-bls-skill.sh "<target-skills-dir>"
```

To install from a different local zip:

```bash
BCE_BLS_SKILL_ZIP="/path/to/bce-bls.zip" bash scripts/install-bce-bls-skill.sh "<target-skills-dir>"
```

To force a remote update from the official package or a mirror:

```bash
BCE_BLS_SKILL_URL="https://bls-skill.bj.bcebos.com/latest/bce-bls.zip" bash scripts/install-bce-bls-skill.sh "<target-skills-dir>"
```

### 3. Verify Installation

Check that the installed skill directory and frontmatter are present:

```bash
test -f "<target-skills-dir>/bce-bls/SKILL.md"
sed -n '1,40p' "<target-skills-dir>/bce-bls/SKILL.md"
find "<target-skills-dir>/bce-bls" -maxdepth 3 -type f | sort
```

If the agent has a skill-list command, run it and confirm `bce-bls` appears. If it does not appear, restart or reload the agent so it rescans the skills directory.

### 4. Configure BLS Credentials Safely

The official BLS skill needs Baidu Cloud AK/SK with read permission for the target log resources. Avoid asking the user to paste long-lived AK/SK in chat.

Prefer environment variables:

```bash
export BCE_BLS_ACCESS_KEY="<ak>"
export BCE_BLS_SECRET_KEY="<sk>"
```

Or use the credentials file:

```text
~/.bce_bls/credentials
```

```ini
[default]
bce_access_key_id = DEFAULT_AK
bce_secret_access_key = DEFAULT_SK

[prod]
bce_access_key_id = PRODUCTION_AK
bce_secret_access_key = PRODUCTION_SK
```

Use `BCE_BLS_PROFILE` to switch profiles:

```bash
export BCE_BLS_PROFILE=prod
```

### 5. Smoke Test

Ask the target agent to use `bce-bls`, for example:

```text
Use bce-bls to list my BLS projects in region bj.
```

BLS is region-scoped. If the user does not provide a region, ask for one before attempting queries.

## Notes

- The official zip installs a skill named `bce-bls`; do not rename it after extraction unless the target agent requires a different naming convention.
- The target machine needs `python3`; the official document lists it as a prerequisite.
- If `unzip` is missing, install it with the target system package manager or use Python's `zipfile` module as a fallback.
- The installer also accepts the legacy `BLS_SKILL_ZIP` and `BLS_SKILL_URL` aliases.
- Refresh `assets/bce-bls.zip` when the official BLS skill changes; the bundled copy favors portability over always getting the latest remote package.
