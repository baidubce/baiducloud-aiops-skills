# Baidu Cloud Skills

**English** | [简体中文](README-CN.md)

An official Baidu AI Cloud Agent Skills collection that provides AI Agents with rich Baidu AI Cloud product capabilities and general-purpose tools.

## Overview

This repository contains a set of officially maintained Agent Skills designed to help developers use Baidu AI Cloud products and services more efficiently. Each Skill is carefully designed and tested to ensure stability and reliability.

## Skills List

Baidu AI Cloud product Skills will be updated soon.

## Installation

### Install Skills with npx

```bash
# Install a single Skill
npx skills add baidubce/baiducloud-aiops-skills --skill <skill-name>

# Install all Baidu AI Cloud Skills
npx skills add baidubce/baiducloud-aiops-skills

# Install the stable release (default)
npx skills add baidubce/baiducloud-aiops-skills --skill <skill-name>
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/baidubce/baiducloud-aiops-skills.git

# Add a Skill from the local Skills directory
npx skills add <path>/baiducloud-aiops-skills/skills/<skill-name>
```

## Authentication and Configuration

Skills related to Baidu AI Cloud products require authentication configuration. The following authentication methods are supported:

AccessKey authentication

```bash
# Set environment variables
bce configure set \
  --access-key-id YOUR_AK \
  --secret-access-key YOUR_SK \
  --region bj
```

BCE CLI configuration profile authentication

```bash
# ~/.bce/config.json
bce configure use [profile]
```

**Security Note**

- For **`AccessKey authentication`** and **`AK credential authentication through a BCE CLI configuration profile`**, we recommend using them only in local test environments for personal use to avoid exposing plaintext AK/SK credential information.

## License

[Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Copyright (c) 2009-present, Baidu Cloud All rights reserved.

[issue]: https://github.com/baidubce/baiducloud-aiops-skills/issues/new
