# Baidu Cloud Skills

[English](README.md) | **简体中文**

百度智能云官方 Agent Skills 集合，为 AI Agent 提供丰富的百度智能云产品能力和通用工具集。

## 概述
本仓库包含了一系列官方维护的 Agent Skills，旨在帮助开发者更高效地使用百度智能云产品和服务。每个 Skill 都经过精心设计和测试，确保稳定性和可靠性。

## Skills 列表
百度智能云产品 Skills 待更新

## 安装

### 使用 npx 安装 Skills

```bash
# 安装单个 Skill
npx skills add baidubce/baiducloud-aiops-skills --skill <skill-name>

# 安装所有百度智能云 Skills
npx skills add baidubce/baiducloud-aiops-skills

# 安装正式版（默认）
npx skills add baidubce/baiducloud-aiops-skills --skill <skill-name>

```

### 手动安装

```bash
# 克隆仓库
git clone https://github.com/baidubce/baiducloud-aiops-skills.git

# 进入 Skills 目录
npx skills add <path>/baiducloud-aiops-skills/skills/<skill-name>

```

## 认证与配置
使用百度智能云产品相关的 Skills 需要配置认证信息。支持以下认证方式：

AccessKey 认证

```bash
# 设置环境变量
bce configure set \
  --access-key-id YOUR_AK \
  --secret-access-key YOUR_SK \
  --region bj
```

BCE CLI 配置文件认证

```bash
# ~/.bce/config.json
bce configure use [profile]
```

**安全提示**

- **`AccessKey 认证`** 和 **`BCE CLI 配置文件认证的 AK 凭证认证`**，建议仅在本地测试环境时个人使用，避免明文 AK/SK 凭证信息的外泄。

## 许可证
[Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Copyright (c) 2009-present, Baidu Cloud All rights reserved.

[issue]: https://github.com/baidubce/baiducloud-aiops-skills/issues/new