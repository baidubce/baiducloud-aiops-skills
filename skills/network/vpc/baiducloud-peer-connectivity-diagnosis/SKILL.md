---
name: baiducloud-peer-connectivity-diagnosis
description: 只读诊断百度智能云 VPC 对等连接无法互通、单向不通或特定 IP/端口不可达问题，核查连接状态、双端 VPC 与子网、对等连接下一跳、正反向路由、安全组和 ACL 证据，并明确跨账号或权限不足造成的验证缺口。用于对等连接配置排障与变更前核查；不得创建、接受、拒绝、修改、续费、调带宽、切换 DNS、释放连接或主动发送业务探测流量。
---

# 百度智能云对等连接连通性配置诊断

## 推荐问法

- “两个 VPC 已建立对等连接但互相访问不了，帮我排查配置。”
- “通过对等连接访问出现单向不通，检查正反向路由是否完整。”
- “某个 IP 或端口无法通过 VPC 对等连接访问，帮我定位原因。”
- “检查对等连接两端的子网路由、安全组和 ACL 是否共同允许这条流量。”
- “这是跨账号对等连接，请标出因为权限不足而无法确认的诊断证据。”

## 只读边界

- 仅执行百度智能云官方 Endpoint 的 HTTPS `GET` 请求及本地报告生成。
- 不执行 `POST`、`PUT`、`PATCH`、`DELETE`，不接受或拒绝跨账号申请，不修改路由、安全组、ACL、DNS、带宽、计费或实例状态。
- 不执行 ping、端口扫描、抓包或业务请求；结论只覆盖控制面配置。
- 不在命令参数、日志、报告或 Skill 包中写入 AK、SK、STS Token 或 Authorization 头。
- 发现缺失配置时给出人工修复方向，不直接实施修复。

## 选择诊断模式

- 用户给出对等连接 ID、源 IP、目的 IP、协议和端口时，使用精确流量路径模式。这是判断策略是否匹配的首选模式。
- 仅给出地域或连接 ID 时，使用拓扑模式：检查连接状态、两端访问覆盖和对等连接路由是否覆盖对端子网，但不判定某个安全组或 ACL 一定阻断流量。
- 源 IP 与目的 IP 必须成对提供。TCP/UDP 的端口只有在同时提供协议时才参与安全策略判断。

## 工作流

1. 确认本端地域；缺少地域时先询问，不扫描所有地域。
2. 读取 [RAM 权限](references/ram-policies.md)。使用子用户或 STS，并仅授予诊断所需只读策略。
3. 读取 [API 与诊断模型](references/api-reference.md)，特别注意：
   - 对等连接两端需要分别配置路由；
   - `nexthopType` 应为 `peerConn`；
   - `nexthopId` 应匹配该端的 `localIfId`，而不是 `peerConnId`；
   - 同地域详情查询要带正确的 `role`。
4. 检查环境变量 `BCE_ACCESS_KEY_ID`、`BCE_SECRET_ACCESS_KEY` 和可选的 `BCE_SESSION_TOKEN`，不得回显。若使用 JSON 凭证文件，文件必须在 Skill 目录外、归当前用户所有且权限为 `600`。
5. 精确诊断示例：

   ```bash
   python3 scripts/peer_connectivity_diagnosis.py \
     --credentials-file /absolute/path/to/credentials.json \
     --regions bj \
     --peer-conn-id peerconn-example \
     --source-ip 10.0.1.10 \
     --destination-ip 192.168.1.20 \
     --protocol tcp \
     --port 443 \
     --output-dir /absolute/path/to/peer-diagnosis
   ```

6. 拓扑模式可省略连接 ID，诊断所选地域中成功列出的全部连接：

   ```bash
   python3 scripts/peer_connectivity_diagnosis.py \
     --regions bj \
     --output-dir /absolute/path/to/peer-diagnosis
   ```

7. 若用户提供已有快照，使用离线模式并保留同样的流量参数：

   ```bash
   python3 scripts/peer_connectivity_diagnosis.py \
     --input examples/sample-connectivity-snapshot.json \
     --source-ip 10.0.1.10 \
     --destination-ip 192.168.1.20 \
     --protocol tcp \
     --port 443 \
     --output-dir /absolute/path/to/peer-diagnosis
   ```

8. 先看报告的覆盖率和结论置信度，再按 [诊断规则](references/diagnostic-rules.md)复核证据。远端不可访问时不得声称远端路由或策略正常。
9. 返回：连接状态、端点覆盖、源/目的子网定位、去向与回向路由、匹配的安全组/ACL 证据、阻断候选、未验证项和人工处理顺序。

## 结论规则

- `active` 只表示连接控制面可用，不证明路由和安全策略正确。
- 双向路由都匹配也不证明业务必然可达；主机防火墙、进程监听、实例状态和应用响应不在本 Skill 的 GET 配置证据中。
- 普通安全组仅在 IP 成功映射到 ENI、关联组被完整获取且协议/端口明确时给出方向性结论。
- ACL 按最小 `position` 优先匹配；无法解析的规则、地址组、企业安全组或未返回字段都会降低置信度。
- VPC CIDR 重叠不自动判为故障。仅当本次通信所涉及的两端子网重叠，或路由选择存在明确歧义时报告风险。

## 输出

- `snapshot.json`：原始只读快照、覆盖率、诊断输入和结构化发现。
- `report.md`：面向排障人员的证据报告。
- 每项结论标记为 `confirmed`、`candidate` 或 `unknown`，并给出地域、端点、连接 ID、规则 ID 和证据字段。
- 报告为空时写“在成功查询且可判定的范围内未发现配置阻断”，不得写“网络一定正常”。

## 本地验证

```bash
python3 scripts/peer_connectivity_diagnosis.py --self-test
python3 scripts/peer_connectivity_diagnosis.py \
  --input examples/sample-connectivity-snapshot.json \
  --source-ip 10.0.1.10 \
  --destination-ip 192.168.1.20 \
  --protocol tcp \
  --port 443 \
  --output-dir /tmp/baiducloud-peer-connectivity-diagnosis
```
