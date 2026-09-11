---
name: baiducloud-bce-bls-skill
description: 从 BLS 官方文档或打包好的 zip 安装并验证百度智能云日志服务（BLS）官方 AI Agent skill（`bce-bls`）。适用于用户需要安装、更新、下载、配置或排查 BLS 安装器 skill（`bce-bls-skill` 或旧名 `bls-skill`）、`bce-bls.zip`、OpenCode/OpenClaw skill 安装，以及通过 AI agent 用自然语言查询百度智能云日志服务等场景。
---

# BCE BLS Skill 安装器

使用本 skill 可将百度智能云日志服务（BLS）官方 AI Agent skill 安装到目标 agent 的 `skills` 目录。安装后的运行时 skill 名为 `bce-bls`；本 `bce-bls-skill` 仅是安装器和验证指南。建议优先使用内置的 `assets/bce-bls.zip` 安装包，这样安装过程不依赖能否访问百度侧的下载地址。

官方参考资料：

- BLS AI Agent 指南：https://cloud.baidu.com/doc/BLS/s/Omnr306y5
- BLS skill zip 包：https://bls-skill.bj.bcebos.com/latest/bce-bls.zip
- 内置安装包：`assets/bce-bls.zip`

## 工作流程

### 1. 确定目标 skills 目录

根据用户正在使用的 agent 推断目标目录：

```text
OpenCode: ~/.config/opencode/skills
OpenClaw: {openclaw_path}/skills
Hermes: ~/.hermes/skills
Codex: ~/.codex/skills or $CODEX_HOME/skills
Other agents: the agent's documented skills directory
```

如果无法推断出目标目录，直接询问用户。除非用户明确希望在代码仓库中保留一份副本，否则不要安装到当前代码仓库中。

### 2. 优先使用原生包安装方式

对于 OpenClaw，官方文档说明用户可以直接用以下命令安装本安装器 skill：

```bash
openclaw skills install bce-bls-skill
```

如需可移植的安装方式，请使用内置的安装脚本。该脚本在 `assets/bce-bls.zip` 存在时优先从内置包安装，只有内置包缺失时才回退到官方下载地址：

```bash
bash scripts/install-bce-bls-skill.sh "<target-skills-dir>"
```

从其他本地 zip 包安装：

```bash
BCE_BLS_SKILL_ZIP="/path/to/bce-bls.zip" bash scripts/install-bce-bls-skill.sh "<target-skills-dir>"
```

强制从官方包或镜像源做远程更新：

```bash
BCE_BLS_SKILL_URL="https://bls-skill.bj.bcebos.com/latest/bce-bls.zip" bash scripts/install-bce-bls-skill.sh "<target-skills-dir>"
```

### 3. 验证安装结果

检查安装后的 skill 目录和 frontmatter 是否存在：

```bash
test -f "<target-skills-dir>/bce-bls/SKILL.md"
sed -n '1,40p' "<target-skills-dir>/bce-bls/SKILL.md"
find "<target-skills-dir>/bce-bls" -maxdepth 3 -type f | sort
```

如果目标 agent 提供了 skill 列表命令，执行该命令并确认 `bce-bls` 已出现在列表中。若未出现，请重启或重新加载 agent，让它重新扫描 skills 目录。

### 4. 安全地配置 BLS 凭据

BLS 官方 skill 需要具备目标日志资源读权限的百度智能云 AK/SK。请避免让用户在对话中直接粘贴长期有效的 AK/SK。

推荐使用环境变量：

```bash
export BCE_BLS_ACCESS_KEY="<ak>"
export BCE_BLS_SECRET_KEY="<sk>"
```

也可以使用凭据文件：

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

通过 `BCE_BLS_PROFILE` 切换 profile：

```bash
export BCE_BLS_PROFILE=prod
```

### 5. 冒烟测试

让目标 agent 调用 `bce-bls`，例如：

```text
Use bce-bls to list my BLS projects in region bj.
```

BLS 是按地域隔离的。如果用户没有提供地域，先询问地域再发起查询。

## 注意事项

- 官方 zip 包安装的 skill 名为 `bce-bls`；除非目标 agent 要求不同的命名规范，解压后不要重命名。
- 目标机器需要有 `python3`；官方文档将其列为前置依赖。
- 如果缺少 `unzip`，请用目标系统的包管理器安装，或改用 Python 的 `zipfile` 模块作为替代方案。
- 安装脚本同时兼容旧的 `BLS_SKILL_ZIP` 和 `BLS_SKILL_URL` 别名。
- 官方 BLS skill 更新时，记得同步刷新 `assets/bce-bls.zip`；内置副本优先保证可移植性，而非始终获取最新的远端包。
