---
name: baiducloud-public-dns-record-audit
description: 只读查询并审计百度智能云智能云解析公网 DNS 的域名与解析记录，检查域名和记录状态、重复记录、同线路 CNAME 冲突、记录值格式、产品版本最小 TTL、MX 优先级、泛解析及默认线路覆盖，生成查询覆盖率与配置质量报告。用于用户要求盘点公网 DNS 配置、检查解析记录质量、排查控制面配置风险或确认只读权限时；不得用于新增、修改、启停、续费、升级或删除域名及解析记录，也不用于验证公网权威解析结果或传播状态。
---

# 百度智能云公网 DNS 解析记录质量审计

## 推荐问法

- “盘点智能云解析中的公网域名和全部 DNS 记录。”
- “检查是否存在重复解析记录或同一主机记录的 CNAME 冲突。”
- “审计 DNS 记录值、TTL、MX 优先级等字段是否合理。”
- “找出停用、异常以及缺少默认线路覆盖的解析记录。”
- “检查泛解析配置和过宽的解析范围，并生成只读风险报告。”

## 坚持只读边界

- 仅向 `https://dns.baidubce.com` 执行域名列表和解析记录列表的 HTTPS `GET` 请求，以及本地读取和报告生成。
- 禁止执行 `POST`、`PUT`、`PATCH`、`DELETE`，禁止新增、修改、启停、续费、升级或删除任何域名和记录。
- 不因账号拥有更高权限而放宽限制；只给出配置事实、规则命中和人工复核建议，不自动整改。
- 不在命令参数、日志、报告或 Skill 包中写入 AK、SK、STS Token、Authorization 头。
- 本 Skill 审计控制面配置快照，不对公网权威应答、递归缓存、DNSSEC、传播状态或业务可用性下结论。

## 执行工作流

1. 阅读 [RAM 权限](references/ram-policies.md)，优先使用仅绑定官方 `DNSReadPolicy` 的 IAM 子用户。
2. 阅读 [API 与字段说明](references/api-reference.md)。公网 DNS 是全局服务，不需要地域参数；用户此前提供的地域不适用于本 Skill。
3. 检查环境变量 `BCE_ACCESS_KEY_ID`、`BCE_SECRET_ACCESS_KEY`；使用 STS 时同时检查 `BCE_SESSION_TOKEN`。不要回显变量值。也可在 Skill 目录外放置权限为 `600` 的 JSON 凭证文件，字段为 `accessKeyId`、`secretAccessKey` 和可选的 `sessionToken`。
4. 将输出目录放在 Skill 目录外。审计账号下全部公网 DNS 域名：

   ```bash
   python3 scripts/public_dns_record_audit.py \
     --output-dir /absolute/path/to/public-dns-audit-output
   ```

   使用受限凭证文件时：

   ```bash
   python3 scripts/public_dns_record_audit.py \
     --credentials-file /absolute/path/to/credentials.json \
     --output-dir /absolute/path/to/public-dns-audit-output
   ```

5. 只检查指定域名时，传入逗号分隔的精确域名。脚本仍会查询域名列表并在本地做精确匹配，避免 API 模糊搜索误纳入相似域名：

   ```bash
   python3 scripts/public_dns_record_audit.py \
     --zones example.com,example.net \
     --output-dir /absolute/path/to/public-dns-audit-output
   ```

6. 若用户仅提供已有 JSON 快照，使用离线模式：

   ```bash
   python3 scripts/public_dns_record_audit.py \
     --input /absolute/path/to/public-dns-snapshot.json \
     --output-dir /absolute/path/to/public-dns-audit-output
   ```

7. 先检查“采集覆盖率”。域名列表失败意味着无法盘点账号；单个域名的记录查询失败只能标记该域名覆盖不完整，不能当成零记录。
8. 依据 [审计规则](references/audit-rules.md)复核发现。多值 A/AAAA/MX 本身合法；`stopped` 可能是计划内暂停；私网地址也可能是有意发布，相关提示不得直接判为故障。
9. 返回：查询范围、域名和记录数量、覆盖率、状态/类型/线路分布、规则发现、限制和人工建议。

## 输出要求

- `inventory.json` 保存 API 原始字段、查询覆盖率和分析结果；`report.md` 保存中文审计报告。
- 每条发现包含规则编号、严重度、域名、记录 ID、主机记录、类型、线路、事实、解释和证据。
- 未知状态、记录类型和字段必须保留并提示人工解释，不得静默丢弃。
- 没有发现时只能说“在成功查询且规则覆盖的配置范围内未发现命中”，不得声称 DNS 一定正常。
- 域名、记录值、标签和配置拓扑不得发送到未获用户授权的外部服务。

## 失败处理

- `401`：检查凭证、STS Token 和系统时间，不要求用户在对话中粘贴密钥。
- `403`：确认绑定 `DNSReadPolicy`，保留成功结果并标记覆盖不完整。
- `404`：核对 Endpoint、域名和 API 版本；不得改用写接口试探。
- `429` 或 `5xx`：脚本仅对相同的 GET 请求做有限退避重试。
- 某域名的记录查询失败时保留域名及失败证据，不把该域名标记为“无记录”。

## 本地验证

以下命令不访问云环境：

```bash
python3 scripts/public_dns_record_audit.py --self-test
python3 scripts/public_dns_record_audit.py \
  --input examples/sample-public-dns.json \
  --output-dir /tmp/baiducloud-public-dns-record-audit
```
