---
name: baiducloud-vpc-security-policy-audit
description: 只读查询并审计百度智能云 VPC 普通安全组、企业安全组与网络 ACL 配置，识别公网暴露、敏感端口开放、全协议全端口、宽泛出站、重复规则及优先级遮蔽风险。用于安全组或 ACL 配置核查、暴露面排查、规则冲突分析和合规巡检；不得用于添加、修改、删除、绑定或解绑任何规则或资源。
---

# 百度智能云 VPC 安全策略巡检

## 推荐问法

- “审计这个 VPC 的安全组、企业安全组和网络 ACL 配置风险。”
- “找出对公网开放 SSH、RDP、数据库等敏感端口的规则。”
- “检查安全策略中是否存在全协议全端口、宽泛出站或重复规则。”
- “分析安全组和 ACL 是否有规则冲突、优先级遮蔽或实际不生效的配置。”
- “生成一份只读的 VPC 网络访问控制合规巡检报告，不要修改任何规则。”

## 坚持只读边界

- 仅执行官方百度智能云 Endpoint 的 HTTPS `GET` 请求，以及本地 JSON 分析和报告生成。
- 禁止调用 `POST`、`PUT`、`PATCH`、`DELETE`，禁止创建、授权、修改、删除、绑定或解绑安全组与 ACL。
- 即使账号拥有运维或管理权限，也不得放宽只读限制。
- 只输出事实、风险解释和人工整改建议，不实施整改。
- 不在参数、日志、报告或 Skill 包中保存 AK、SK、STS Token 或 Authorization 头。

## 执行工作流

1. 明确巡检地域；缺少地域时先询问，不扫描所有地域。
2. 阅读 [RAM 权限](references/ram-policies.md)，优先使用只读子用户或 STS 临时凭证。
3. 阅读 [API 与字段说明](references/api-reference.md)，确认普通安全组、企业安全组和 ACL 的字段语义。
4. 阅读 [审计规则](references/audit-rules.md)，根据业务用途解释发现；不得仅凭一条规则断言实例已从公网可达。
5. 使用环境变量 `BCE_ACCESS_KEY_ID`、`BCE_SECRET_ACCESS_KEY` 和可选的 `BCE_SESSION_TOKEN`。若执行环境无法安全继承变量，可在 Skill 目录外创建权限为 `600` 的 JSON 凭证文件，字段为 `accessKeyId`、`secretAccessKey` 和可选的 `sessionToken`，再通过 `--credentials-file` 指定。
6. 将输出目录放在 Skill 目录外，运行只读采集：

   ```bash
   python3 scripts/vpc_security_audit.py \
     --regions bj \
     --output-dir /absolute/path/to/security-audit
   ```

   使用受限凭证文件时：

   ```bash
   python3 scripts/vpc_security_audit.py \
     --credentials-file /absolute/path/to/credentials.json \
     --regions bj \
     --output-dir /absolute/path/to/security-audit
   ```

   仅审计指定 VPC 时增加 `--vpc-ids vpc-id-1,vpc-id-2`。
7. 若用户仅提供规范化 JSON，使用离线模式：

   ```bash
   python3 scripts/vpc_security_audit.py \
     --input /absolute/path/to/security-policies.json \
     --output-dir /absolute/path/to/security-audit
   ```

8. 先查看报告的“采集覆盖率”。任何资源类型查询失败时，将结论标记为不完整；不得把“查询失败”解释为“没有规则”。
9. 返回巡检地域、覆盖率、策略数量、按严重度汇总的发现、证据字段、判断限制和人工建议。

## 解释发现

- “公网源”仅指 `all`、`0.0.0.0/0` 或 `::/0`；参数模板、地址组和嵌套安全组不直接判定为公网。
- 普通安全组规则是允许规则；企业安全组和 ACL 需同时检查 `action` 与优先级。
- 安全组允许不等于公网真实可达；还需结合公网 IP、负载均衡、路由、实例监听状态及其他关联安全策略人工确认。
- 宽泛出站规则在平台默认配置中可能是预期行为，只作为低风险治理项，不宣称存在数据泄露。
- 对重复、遮蔽或同优先级冲突只提出复核建议，不自动删除或调整规则。

## 输出要求

- `inventory.json`：机器可读的采集快照和分析结果。
- `report.md`：面向用户的覆盖率、汇总和风险报告。
- 每条发现包含地域、策略类型、策略 ID、规则 ID、方向、远端地址、协议、端口及触发规则编号。
- 没有发现时写明“在成功采集且已实现的规则范围内未发现问题”，不得声明账号绝对安全。

## 失败处理

- `401`：检查凭证、STS Token 与本机时间，不要求用户把密钥粘贴到对话中。
- `403`：列出失败资源类型及缺少的只读系统策略，保留其他成功结果。
- `404`：核对地域 Endpoint 和 API 版本，不使用写接口试探。
- `429` 或 `5xx`：允许对同一 GET 请求退避重试，不改变请求方法。
- 普通安全组、企业安全组或 ACL 任一覆盖不完整时，报告必须明确标注限制。

## 本地验证

```bash
python3 scripts/vpc_security_audit.py --self-test
python3 scripts/vpc_security_audit.py \
  --input examples/sample-security-policies.json \
  --output-dir /tmp/baiducloud-vpc-security-policy-audit
```
