---
name: baiducloud-csn-route-relationship-audit
description: 只读查询并审计百度智能云云智能网 CSN 路由表、网络实例、关联关系、学习关系和路由条目，生成按 CSN/路由表聚合的路由控制面拓扑、查询覆盖率、冲突与孤立引用报告。用于用户要求排查 CSN 路由表配置、关联或学习缺失、冲突/黑洞路由、异常引用和路由隔离边界时；不得创建、修改或删除任何关系、路由表、路由或云资源，也不能证明数据面可达。
---

# 百度智能云 CSN 路由关联与传播配置排查

## 推荐问法

- “盘点这个 CSN 的路由表、关联关系、学习关系和路由条目。”
- “检查 CSN 中是否存在冲突路由或黑洞路由。”
- “找出已加载但没有关联关系或学习关系的网络实例。”
- “检查路由表中是否存在孤立挂载引用、重复关系或父级 ID 不一致。”
- “分析自定义路由表的隔离边界，并找出可能闲置的路由表。”

## 只读边界

- 仅向 `https://csn.baidubce.com` 执行 CSN 列表、网络实例列表、路由表列表、关联关系、学习关系和路由条目 HTTPS `GET` 请求。
- 禁止 `POST`、`PUT`、`PATCH`、`DELETE`；禁止创建、修改或删除路由表、关联关系、学习关系、路由条目、网络实例、带宽包及地域带宽。
- 不因账号拥有更高权限而放宽限制。只输出控制面事实、查询覆盖率、规则发现和人工复核建议。
- 不在命令参数、日志、报告或 Skill 包中写入 AK、SK、STS Token、Authorization 头。
- 不探测业务流量，不查询 VPC 内路由表、安全组、ACL、专线 CPE、带宽或路由策略，不能据此证明端到端可达。

## 执行工作流

1. 阅读 [RAM 权限](references/ram-policies.md)，优先使用仅绑定官方 `CSNReadOnlyAccessPolicy` 的 IAM 子用户或受限 STS 凭证。
2. 阅读 [API 与字段说明](references/api-reference.md)。CSN 是全局服务，不需要地域请求参数。
3. 检查环境变量 `BCE_ACCESS_KEY_ID`、`BCE_SECRET_ACCESS_KEY`；使用 STS 时同时检查 `BCE_SESSION_TOKEN`，不要回显。也可在 Skill 目录外使用权限为 `600` 的 JSON 凭证文件，字段为 `accessKeyId`、`secretAccessKey` 和可选 `sessionToken`。
4. 将输出目录放在 Skill 目录外，审计账号可见的全部 CSN：

   ```bash
   python3 scripts/csn_route_relationship_audit.py \
     --output-dir /absolute/path/to/csn-route-audit-output
   ```

   使用受限凭证文件时：

   ```bash
   python3 scripts/csn_route_relationship_audit.py \
     --credentials-file /absolute/path/to/credentials.json \
     --output-dir /absolute/path/to/csn-route-audit-output
   ```

5. 只审计指定 CSN 时，使用逗号分隔的精确 ID；未匹配 ID 必须作为覆盖缺口报告：

   ```bash
   python3 scripts/csn_route_relationship_audit.py \
     --csn-ids csn-aaa,csn-bbb \
     --output-dir /absolute/path/to/csn-route-audit-output
   ```

6. 使用已有快照时进入离线模式：

   ```bash
   python3 scripts/csn_route_relationship_audit.py \
     --input /absolute/path/to/csn-route-snapshot.json \
     --output-dir /absolute/path/to/csn-route-audit-output
   ```

7. 先核对“查询覆盖率”。列表或某张路由表的任一子查询失败时，该范围未知，不能按零关系或零路由解释。
8. 依据 [审计规则](references/audit-rules.md)复核发现。缺少关系可能是有意隔离；`blackHole=true` 也可能是有意丢弃，报告不得擅自改动。
9. 返回：CSN/路由表/网络实例数量，关联和学习矩阵，路由状态/类型/地域分布，冲突与黑洞路由，孤立引用，查询缺口、限制和人工建议。

## 输出要求

- `inventory.json` 保存原始 API 字段、每层查询状态和分析结果；`report.md` 保存中文排查报告。
- 每条发现包含规则编号、严重度、CSN/路由表/挂载/路由标识、事实、解释和证据。
- 对每张路由表分别保存 `_associationsStatus`、`_propagationsStatus`、`_rulesStatus`；查询失败不得伪装成空数组。
- 未知状态、类型和字段必须保留，不得静默丢弃。
- 没有发现时只能说“在成功查询且规则覆盖的控制面范围内未发现命中”，不得声称全网互通或无风险。
- 账号 ID、网络实例标识、标签、网段和路由拓扑不得发送到未获用户授权的外部服务。

## 失败处理

- `401`：检查凭证、STS Token 和系统时间，不要求用户在对话中粘贴密钥。
- `403`：确认绑定 `CSNReadOnlyAccessPolicy`；若路由查询仍被拒绝，在 IAM 控制台核对该租户的只读动作范围，禁止改授运维/全控策略作为自动补救。
- `404`：核对 Endpoint、CSN ID、路由表 ID 和 API 版本，不得改用写接口试探。
- `429` 或 `5xx`：只对相同 GET 请求做有限退避重试。
- 单个 CSN 或路由表查询失败时保留成功结果，继续其他范围并标记覆盖不完整。

## 本地验证

以下命令不访问云环境：

```bash
python3 scripts/csn_route_relationship_audit.py --self-test
python3 scripts/csn_route_relationship_audit.py \
  --input examples/sample-csn-route-relationships.json \
  --output-dir /tmp/baiducloud-csn-route-relationship-audit
```
