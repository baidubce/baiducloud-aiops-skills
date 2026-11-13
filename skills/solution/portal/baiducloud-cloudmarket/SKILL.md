---
name: baiducloud-cloudmarket
description: >
  百度云市场命令行 Skill。当用户需要在百度云市场搜索云服务商品、查看商品规格与价格、
  下单新购、查询订单/支付状态、追踪交付进度，或用自然语言完成"帮我找/买某商品"这类
  购物任务时使用。本 Skill 提供一个零第三方依赖的 Node 运行时脚本，通过 IAM OAuth
  登录态换取 STS 临时凭证并以 bce-auth-v1 签名调用 bce-cloudmarket-service，完成
  搜索、详情、下单、收银台链接生成、订单取消与查询。触发词：云市场、商品搜索、买商品、
  下单、见微、iForm、订单状态、交付记录、cloudmarket、bce-cloudmarket。真实支付为
  不可逆扣款，必须由用户在收银台手动确认，本 Skill 不代为支付。
---

# Cloudmarket（百度云市场命令行）

本 Skill 采用**服务层 + 客户层**两层结构（均在包内，零第三方依赖）：

- **服务层 `scripts/service.mjs`**：封装云市场全部内部细节（IAM 登录态、STS 换
  临时凭证、bce-auth-v1 签名、bce-cloudmarket-service 的 REST 契约、订单归属
  校验），对外只导出语义化业务函数（`searchProducts`/`getProduct`/`createOrder`/
  `getPaymentInfo`/`cancelOrder`/`getRecord`/`checkAuthState`/`buildPayUrl`/`login`）与
  领域错误类型。
- **客户层 `scripts/cloudmarket.mjs`**：只 `import ./service.mjs`，负责命令行解析、
  dry-run/确认交互、输出与退出码映射；**对底层签名/STS/后端不可见**。

Skill 负责意图理解与流程编排，真实后端请求与签名由服务层完成——**不自行实现
签名，也不把凭证暴露给用户**。

## 前置条件

调用任何写命令或真实数据前，确认两点（否则先引导用户，不要索要凭证）：

1. **Node.js ≥ 18** 在 `PATH` 上（脚本用内建 fetch/undici/crypto）。
2. **已完成 IAM 登录**。先查登录态：
   ```bash
   node scripts/cloudmarket.mjs auth-status
   ```
   若 `logged_in` 为 false，直接用 `login` 命令发起浏览器登录（见下），token 写入
   `~/.config/cloudmarket/.cli_token_<env>.json` 后即可重试。登录态失效时业务命令
   默认也会自动发起登录并重试一次（无头/CI 环境用 `--no-auto-login` 关闭）。

## 环境变量（正式包已预置，无需手动设置）

从 OneTool 安装的是正式环境（prod）包，以下地址已在打包时预置为正式环境默认值，**装好即可用，
不需要再设置任何环境变量或 `.env`**：

- `MKT_SERVICE_BASE_URL`：云市场后端地址（已预置为正式环境后端）
- `IAM_ENV`：已预置为 `prod`
- `IAM_PUBLIC_BASE`：IAM 域名（已预置为 `https://console.bce.baidu.com`）
- `STS_BASE`：STS 域名（已预置为正式环境 STS）
- `IAM_CLIENT_ID`：OAuth client_id（已预置为 `mkt-cli`）
- `CASHIER_BASE`：收银台域名，用于拼接 `pay_url`（已预置为 `https://console.bce.baidu.com`）
- `MARKET_WEB_BASE_URL`：商品搜索/详情接口域名（已预置为 `https://market.baidu.com`）

只有需要**覆盖**默认地址时才设置同名环境变量（环境变量始终优先）。其他可选项：
`CLI_TOKEN_FILE`、`CLOUDMARKET_AUTO_LOGIN`、`TOKEN_STORE_CA_BUNDLE`。

> 预置值均为基础设施域名、非密钥。

## 命令

只读：
```bash
node scripts/cloudmarket.mjs auth-status                 # 登录态（不含凭证）
node scripts/cloudmarket.mjs search 见微 --page-size 5    # 搜索（可选 --category --delivery-type --min-price --max-price --page）
node scripts/cloudmarket.mjs product <product_id>        # 详情与规格(sku)
node scripts/cloudmarket.mjs order <order_id>            # 订单状态
node scripts/cloudmarket.mjs record <record_id>         # 交付记录
```

登录（主动发起 IAM OAuth 浏览器登录，走授权码 + PKCE，token 原子写入 token 文件）：
```bash
node scripts/cloudmarket.mjs login                       # 按 IAM_ENV 发起登录
node scripts/cloudmarket.mjs login --env prod            # 指定环境
node scripts/cloudmarket.mjs login --no-open             # 只打印授权链接，不自动开浏览器
```

> `login` 做的是**完整授权码流程**，与 refresh_token 是否过期无关——因此
> refresh_token 失效后同样用它重新登录。登录态失效时，其它业务命令**默认会
> 自动发起一次 login 并重试**；无头/CI 环境请加 `--no-auto-login`（或设
> `CLOUDMARKET_AUTO_LOGIN=0`），因为服务器弹不出浏览器会一直等回调到超时。

写操作（默认 dry-run 预览；确认后加 `--yes` 才执行）：
```bash
node scripts/cloudmarket.mjs order-create --product <pid> --sku <packageId:periodId> [--quantity N]
node scripts/cloudmarket.mjs order-create --product <pid> --sku <...> --yes    # 真正下单，成功后自动在浏览器打开收银台
node scripts/cloudmarket.mjs pay-url <order_id>          # 生成收银台链接并在浏览器打开（不扣款）
node scripts/cloudmarket.mjs order-cancel <order_id> --yes
```

`order-create --yes` 与 `pay-url` 拿到 `pay_url` 后会自动用系统浏览器打开收银台（输出里
`browser_opened` 表示是否已尝试打开）；无头环境加 `--no-open` 只打印链接。打开收银台本身不扣款。

`sku_id` 为复合键 `packageId:periodId`，从 `product` 命令的 skus 里取，原样传入。

## 典型流程

1. `auth-status` → 确认已登录（未登录则 `login` 发起浏览器登录，或让业务命令自动触发）
2. `search <关键词>` → 向用户展示候选商品
3. `product <pid>` → 取规格与价格，让用户选规格
4. 向用户确认「商品/规格/金额」→ `order-create ... --yes` 创建订单
5. 收银台会自动在浏览器打开（未弹出则把 `pay_url` 给用户）→ 用户在收银台手动支付
6. 按需 `order` / `record` 追踪状态；不买则 `order-cancel ... --yes`

## 安全边界

- **写操作（下单/支付/取消）前必须向用户确认**；order-create/order-cancel 默认 dry-run，
  只有加 `--yes` 才真正执行。真实支付不可逆，只能由用户在收银台点确认。
- 不索要、不打印任何凭证（API Key、AK/SK、STS Token、Authorization 头、refresh_token）。
  `auth-status` 只返回状态、不返回凭证内容。
- prod 环境未登录时命令会报错或自动发起登录引导用户在浏览器完成授权，不要绕过；
  自动登录仅在能弹出浏览器的交互环境启用，无头/CI 用 `--no-auto-login` 关闭。
- 只调用内置脚本，不自行实现 BCE 签名或直接构造后端请求。
- 下单/取消/查记录按订单归属校验，不操作非当前调用方的订单。
- 脚本仅从 `MKT_SERVICE_BASE_URL` / `IAM_*` / `STS_BASE` 等环境变量取地址，不硬编码域名。
