#!/usr/bin/env node
// cloudmarket —— 百度云市场命令行（客户层 / client layer）
//
// 本文件是「客户层」：只负责解析命令行、处理用户交互（dry-run/确认）、格式化
// 输出与退出码映射。所有云市场底层细节（IAM 登录态、STS 换凭证、bce-auth-v1
// 签名、后端 REST 契约、订单归属校验）都封装在服务层 ./service.mjs 中，本层
// **对底层不可见**——只 import 服务层导出的语义函数与领域错误类型。
//
// 用法：
//   node cloudmarket.mjs <command> [args] [--flags]
//   node cloudmarket.mjs help
//
// 只读命令：auth-status, search, product, order, record
// 登录命令：login（主动发起 IAM OAuth 浏览器登录，refresh_token 过期后也可重登）
// 写操作命令（默认 --dry-run 预览，加 --yes 才执行）：order-create, order-cancel
// pay-url / order-create 拿到收银台链接后自动在浏览器打开（--no-open 关闭）。
//
// 真实模式需先完成 IAM 登录；真实支付不可逆，本脚本不代为支付。
// 登录态失效时默认会自动发起登录并重试一次（可用 --no-auto-login 或
// CLOUDMARKET_AUTO_LOGIN=0 关闭，适合无头/CI 环境）。

import process from 'node:process';
import * as svc from './service.mjs';

// ── 参数解析：位置参数 + --flag / --flag=value ──────────────────────────────
function parseArgs(argv) {
  const positionals = [];
    const flags = {};
  for (let i = 0; i < argv.length; i += 1) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const body = a.slice(2);
      const eq = body.indexOf('=');
      if (eq >= 0) {
        flags[body.slice(0, eq)] = body.slice(eq + 1);
      } else if (i + 1 < argv.length && !argv[i + 1].startsWith('--')) {
        flags[body] = argv[i + 1];
        i += 1;
      } else {
        flags[body] = true;
      }
    } else {
      positionals.push(a);
    }
  }
  return { positionals, flags };
}

function out(o) {
  console.log(typeof o === 'string' ? o : JSON.stringify(o, null, 2));
}

function die(msg, code = 1) {
  console.error(`cloudmarket: ${msg}`);
  process.exit(code);
}

function confirmOrDryRun(action, payload, flags) {
  if (!flags.yes) {
    out({ dry_run: true, action, payload, hint: '预览（dry-run）。确认后加 --yes 真正执行；写操作不可逆。' });
    return false;
  }
  return true;
}

const HELP = `cloudmarket —— 百度云市场命令行（客户层，业务能力在 service.mjs）

用法：node cloudmarket.mjs <command> [args] [--flags]

只读命令：
  auth-status                          查看 IAM 登录态（不含凭证）
  stats [--date YYYY-MM-DD] [--report] 使用度量：按账号统计当日登录/各命令调用次数；每条命令结束后已自动增量上报
                                       （CLOUDMARKET_AUTO_REPORT=0 关闭），--report 立即手动补报
  search <keyword> [--page-size N]     搜索商品（--cid --category --delivery-type --min-price --max-price --page）
  product <product_id>                 商品详情与规格(sku)
  order <order_id>                     订单状态
  record <record_id>                   交付记录

登录命令：
  login [--env <env>] [--account-id <id>] [--port <n>] [--no-open]
                                       主动发起 IAM OAuth 浏览器登录并写 token
                                       （token 未过期且登录人(account_id)一致则免登直接复用；
                                        refresh_token 过期后同样可用它重新登录；
                                        --port 固定回调端口（SSH 隧道/远端登录用）；
                                        --no-open 只打印授权链接不自动开浏览器）

写操作（order-create / order-cancel 默认 dry-run，加 --yes 执行）：
  order-create --product <pid> --sku <packageId:periodId> [--quantity N] [--no-open]
                                       下单成功后自动在浏览器打开收银台（--no-open 只打印链接）
  pay-url <order_id> [--no-open]       生成收银台链接并在浏览器打开（不扣款）
  order-cancel <order_id>

全局开关：
  --no-auto-login                      关闭"登录态失效自动发起登录并重试"（无头/CI 用）
                                       等价于环境变量 CLOUDMARKET_AUTO_LOGIN=0

说明：真实模式需先完成 IAM 登录；真实支付不可逆，本脚本不代为支付。`;

// 登录态失效时是否自动发起登录：默认开启，--no-auto-login 或 CLOUDMARKET_AUTO_LOGIN=0 关闭。
function resolveAutoLogin(flags) {
  if (flags['no-auto-login']) {
    return false;
  }
  const env = (process.env.CLOUDMARKET_AUTO_LOGIN ?? '').trim().toLowerCase();
  if (['0', 'false', 'no', 'off'].includes(env)) {
    return false;
  }
  return true;
}

// 登录提示统一走 stderr，保持 stdout 只输出结构化数据（JSON）。
function printLoginPrompt({ authUrl, opened, env, clientId }) {
  console.error(`cloudmarket: 发起 IAM 登录（env=${env} client_id=${clientId}）`);
  console.error(
    opened
      ? 'cloudmarket: 已尝试在系统浏览器打开登录页，若未弹出请手动访问下方链接：'
      : 'cloudmarket: 请在浏览器手动访问下方链接完成登录：',
  );
  console.error(authUrl);
  console.error('cloudmarket: 正在等待浏览器回调…');
}

// 收银台链接提示同样走 stderr，stdout 只保留 JSON。
function printPayPrompt(payUrl, opened) {
  if (!payUrl) {
    return;
  }
  console.error(
    opened
      ? 'cloudmarket: 已尝试在系统浏览器打开收银台，若未弹出请手动访问下方链接：'
      : 'cloudmarket: 请在浏览器手动访问下方收银台链接完成支付：',
  );
  console.error(payUrl);
}

// 真正执行各命令；登录态/凭证相关错误直接抛出，交 main 决定是否自动登录重试。
async function runCommand(command, positionals, flags, apiKey) {
  switch (command) {
    case undefined:
    case 'help':
    case '--help':
    case '-h':
      out(HELP);
      break;
    case 'auth-status':
      out(svc.checkAuthState());
      break;
    case 'stats': {
      // 使用度量：本地汇总（当日/指定日）；--report 立即签名上报未报增量（不带 --date 时补报所有日期）
      const date = flags.date || svc.metricsLocalDate();
      if (flags.report) {
        out(await svc.reportUsage(flags.date || null));
        break;
      }
      out(svc.metricsSummary(date));
      break;
    }
    case 'login': {
      const info = await svc.login({
        env: flags.env,
        open: !flags['no-open'],
        onPrompt: printLoginPrompt,
        accountId: flags['account-id'] || process.env.MKT_LOGIN_ACCOUNT_ID || null,
        port: flags.port ? Number(flags.port) : 0,
      });
      out({
        ...info,
        note: info.skipped
          ? 'token 未过期且登录人一致，已复用现有登录态，无需重新登录。'
          : '登录成功，token 已写入。refresh_token 过期后可再次运行 login 重新登录。',
      });
      break;
    }
    case 'search': {
      const r = await svc.searchProducts({
        keyword: positionals[0] || flags.keyword,
        category: flags.category,
        deliveryType: flags['delivery-type'],
        minPrice: flags['min-price'],
        maxPrice: flags['max-price'],
        cid: flags.cid != null ? flags.cid : 0,
        page: flags.page ? Number(flags.page) : 1,
        pageSize: flags['page-size'] ? Number(flags['page-size']) : 10,
      });
      out(r);
      break;
    }
    case 'product': {
      if (!positionals[0]) {
        die('缺少 product_id');
      }
      const p = await svc.getProduct(positionals[0]);
      if (!p) {
        die(`商品不存在：${positionals[0]}`, 2);
      }
      out(p);
      break;
    }
    case 'order': {
      if (!positionals[0]) {
        die('缺少 order_id');
      }
      const info = await svc.getPaymentInfo(positionals[0], apiKey);
      if (!info) {
        die(`订单不存在或无权访问：${positionals[0]}`, 2);
      }
      out(info);
      break;
    }
    case 'record': {
      if (!positionals[0]) {
        die('缺少 record_id');
      }
      const rec = await svc.getRecord(positionals[0], apiKey);
      if (!rec) {
        die(`交付记录不存在或无权访问：${positionals[0]}`, 2);
      }
      out(rec);
      break;
    }
    case 'order-create': {
      if (!flags.product || !flags.sku) {
        die('缺少参数：--product <pid> --sku <packageId:periodId>');
      }
      const items = [
        { product_id: flags.product, sku_id: flags.sku, quantity: flags.quantity ? Number(flags.quantity) : 1 },
      ];
      if (!confirmOrDryRun('创建订单（正式环境真实下单，INIT 待支付）', { items }, flags)) {
        break;
      }
      const order = await svc.createOrder({ items, apiKey });
      const opened = flags['no-open'] ? false : svc.openPayUrl(order.pay_url);
      printPayPrompt(order.pay_url, opened);
      out({
        ...order,
        browser_opened: opened,
        note: '订单已创建（待支付）。已尝试在浏览器打开 pay_url，请在收银台手动完成支付；真实扣款不可逆。',
      });
      break;
    }
    case 'pay-url': {
      if (!positionals[0]) {
        die('缺少 order_id');
      }
      const payUrl = svc.buildPayUrl(positionals[0]);
      const opened = flags['no-open'] ? false : svc.openPayUrl(payUrl);
      printPayPrompt(payUrl, opened);
      out({
        order_id: positionals[0],
        pay_url: payUrl,
        browser_opened: opened,
        note: '打开链接本身不扣款，需在收银台手动确认。',
      });
      break;
    }
    case 'order-cancel': {
      if (!positionals[0]) {
        die('缺少 order_id');
      }
      if (!confirmOrDryRun('取消订单（未支付前取消不扣款）', { order_id: positionals[0] }, flags)) {
        break;
      }
      out(await svc.cancelOrder(positionals[0], apiKey));
      break;
    }
    default:
      die(`未知命令：${command}。运行 'help' 查看用法。`, 2);
  }
}

// 可计入度量的命令；未知命令（拼写错误等）不计数，避免统计里出现无意义的功能名。
const METRIC_COMMANDS = new Set([
  'auth-status',
  'stats',
  'login',
  'search',
  'product',
  'order',
  'record',
  'order-create',
  'pay-url',
  'order-cancel',
]);

async function main() {
  const argv = process.argv.slice(2);
  const command = argv[0];
  // 记录一次调用（best-effort）。账号取记录时的登录态：未登录触发自动登录的那次调用
  // 也能归到新登录的账号。正常结束时先记再自动上报；die() 提前退出由 exit 钩子补记，
  // 增量留到下次命令上报。
  const feature =
    !command || command === 'help' || command === '--help' || command === '-h'
      ? 'help'
      : METRIC_COMMANDS.has(command)
        ? command
        : null;
  let recorded = false;
  const recordOnce = () => {
    if (!feature || recorded) {
      return;
    }
    recorded = true;
    try {
      svc.recordCall(feature, svc.checkAuthState().account_id || null);
    } catch {
      /* ignore */
    }
  };
  process.once('exit', recordOnce);
  const { positionals, flags } = parseArgs(argv.slice(1));
  const apiKey = flags['api-key'] || (process.env.API_KEYS || '').split(',')[0].trim() || 'skill-cli';
  const autoLogin = resolveAutoLogin(flags);
  // login/auth-status 自身不触发自动登录重试，避免递归/无意义循环。
  const canAutoLogin = autoLogin && command !== 'login' && command !== 'auth-status';
  let triedLogin = false;

  for (;;) {
    try {
      await runCommand(command, positionals, flags, apiKey);
      recordOnce();
      await svc.autoReportUsage();
      return;
    } catch (e) {
      const isLoginErr = e instanceof svc.LoginRequiredError || e instanceof svc.CliTokenExpiredError;
      if (isLoginErr && canAutoLogin && !triedLogin) {
        triedLogin = true;
        console.error(
          'cloudmarket: 登录态失效，正在自动发起登录…（关闭：--no-auto-login 或 CLOUDMARKET_AUTO_LOGIN=0）',
        );
        try {
          // 自动重登由"登录态失效"触发：强制真正重新授权，不走免登短路
          // （本地 token 可能看似未过期但已被服务端拒绝）。
          const info = await svc.login({
            env: flags.env,
            open: !flags['no-open'],
            onPrompt: printLoginPrompt,
            accountId: flags['account-id'] || process.env.MKT_LOGIN_ACCOUNT_ID || null,
            port: flags.port ? Number(flags.port) : 0,
            force: true,
          });
          console.error(`cloudmarket: 登录成功（env=${info.env}），重试命令…`);
          continue;
        } catch (le) {
          die(le.message, 3);
        }
      }
      // 领域错误 → 退出码映射（客户层只认服务层导出的错误类型，不碰底层实现）
      if (isLoginErr) {
        die(e.message, 3);
      }
      if (e instanceof svc.HttpStatusError) {
        die(`后端返回 HTTP ${e.status}：${String(e.body).slice(0, 300)}`, 4);
      }
      if (e instanceof svc.PermissionDeniedError) {
        die(e.message, 5);
      }
      die(e.message || String(e), 1);
    }
  }
}

main();
