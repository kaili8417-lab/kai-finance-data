# 财务流水看板 — 部署包

> 个人消费 / 不动产 / 收入一体化看板（人民币 + 加币，固定汇率 1 加币 = 5 元）
> 数据周期：2026 年 4–6 月（含部分预付到 8 月的房租）

## 一、文件夹结构

- `index.html` —— 看板本体（单文件，双击即可本地打开；也可直接部署）
- `raw-data/` —— 原始账单备份
  - 支付宝_明细_2026-04至06.csv
  - CIBC_Visa_账单_Apr9-May8.pdf / May9-Jun8.pdf
  - BMO_支票_账单_Apr17.pdf / May19.pdf
  - BMO_储蓄_账单_May19.pdf
  - （微信、建行、CIBC 更早期账单的原始文件未在本次会话保留；其数据已并入 processed-data 内）
- `processed-data/` —— 已清洗归类的结构化数据（真正的"数据库"）
  - clean_data.json —— 人民币三账户（支付宝/微信/建行）已去重、归类、排除后的消费
  - cibc_cad.json / bmo_cad.json —— 加币两账户个人消费
  - cibc_visa_raw.json —— CIBC Visa 三期账单解析底稿
  - props_data.json —— 三处不动产明细
  - income_data.json —— 收入（工资 + 公司返现）
- `pipeline/` —— 处理脚本（build.py 把上面 JSON 合成 index.html）

## 二、部署到 Cloudflare Pages（Direct Upload，约 2 分钟）

1. 登录 https://dash.cloudflare.com → 左侧 **Workers & Pages** → **Create** → **Pages** → **Upload assets**
2. 项目命名（如 `kai-finance`），把 **整个文件夹** 或至少 `index.html` 拖进去上传
3. 点 **Deploy**，几秒后得到一个 `https://kai-finance.pages.dev` 地址
4. （可选）在 Pages 项目设置里加 Access 密码保护，避免公开

> 也可用命令行：`npx wrangler pages deploy ./财务看板`

## 三、每月更新流程

1. 把当月原始账单（支付宝/微信/建行/CIBC/BMO）发给 Claude
2. Claude 按已存记忆规则自动：去重 → 排除生意/转账/投资 → 归类 → 归到对应房产/收入
3. 不确定的明细 Claude 发你确认；没出现过的新商户你补充规则
4. Claude 重新生成 index.html，你把新文件重新上传到 Cloudflare Pages 覆盖

## 四、说明

- 看板数据已**内嵌**在 index.html 里，离线/部署后都能直接看。
- 部署版为只读浏览（页内"添加/导入"的改动刷新后不保存）；正式更新走"每月流程"重发原始数据由 Claude 重建。
- 汇率固定 0.2（1 加币 = 5 元），可在右上角临时调整。
