---
name: cross-border-ops
slug: cross-border-ops
displayName: 跨境运营手册
display_name: 跨境运营手册
display_name_en: Cross-Border Ops Playbook
version: "1.0.0"
description: "跨境运营手册｜跨境电商运营知识层 + 测算层。知识：平台规则与入驻（Amazon/TikTok Shop/Temu/Shopee/AliExpress/独立站）、选品与竞争判断、Listing 与关键词、广告结构与 ACOS 排查、头程与仓配备货、收款结汇与现金流、VAT/EPR/认证与清关合规、核心指标诊断树。测算：本地脚本 cbcalc.py 算到手净利、盈亏平衡售价、盈亏平衡 ACOS、备货量与回款周期。触发词：跨境电商、亚马逊运营、Amazon 选品、TikTok Shop、Temu 半托管、Shopee、独立站、Shopify、Listing 优化、ACOS、CPC、头程、FBA、海外仓、补货、VAT、EPR、CE 认证、清关、收款结汇、利润测算、到手利润。"
description_zh: "跨境运营手册｜跨境电商运营知识层 + 测算层。知识：平台规则与入驻（Amazon/TikTok Shop/Temu/Shopee/AliExpress/独立站）、选品与竞争判断、Listing 与关键词、广告结构与 ACOS 排查、头程与仓配备货、收款结汇与现金流、VAT/EPR/认证与清关合规、核心指标诊断树。测算：本地脚本 cbcalc.py 算到手净利、盈亏平衡售价、盈亏平衡 ACOS、备货量与回款周期。触发词：跨境电商、亚马逊运营、Amazon 选品、TikTok Shop、Temu 半托管、Shopee、独立站、Shopify、Listing 优化、ACOS、CPC、头程、FBA、海外仓、补货、VAT、EPR、CE 认证、清关、收款结汇、利润测算、到手利润。"
description_en: "Cross-Border Ops Playbook: a knowledge layer plus a calculator layer for Chinese cross-border sellers. Knowledge — platform rules and onboarding (Amazon, TikTok Shop, Temu, Shopee, AliExpress, Shopify DTC), product validation and competition screening, listing and keyword structure, ad structure and ACOS troubleshooting, first-leg freight and replenishment planning, payout channels and cash-flow gaps, VAT/EPR/certification and customs compliance, KPI diagnostic trees. Calculator — a local stdlib-only script (cbcalc.py) for net margin per unit, break-even price, break-even ACOS, replenishment quantity and cash-return cycle. Conclusion first, numbers with explicit assumptions, volatile policy facts flagged for verification."
summary: 跨境电商运营知识库加本地测算脚本：平台规则、选品、Listing、广告、物流备货、收款税务合规、指标诊断，外加净利/保本价/保本ACOS/备货量/回款周期计算。
examples_zh:
  - 我准备上 Amazon 美国站，帮我判断这个品能不能做，顺便算清到手利润
  - 我的 ACOS 一直降不下来，帮我按广告结构逐层排查
  - 德国站要不要注册 VAT 和包装法 EPR？不注册会怎样
examples_en:
  - I'm about to launch on Amazon US — is this product viable, and what's my net margin per unit?
  - My ACOS won't come down — walk the ad structure layer by layer
  - Do I need German VAT and packaging EPR registration? What happens if I skip it?
license: MIT
compatibility: 知识层无依赖；测算层需 Python 3.9+（仅标准库）。平台佣金、仓配费、税率、免税额、认证清单等易变事实，执行前必须以卖家后台或官网公告复核。
homepage: https://github.com/dzp181/cross-border-ops-expert
agent_created: true
tags: ["跨境电商", "运营", "选品", "合规"]
category: 电商与跨境
risk_level: L1
metadata:
  author: dzp181
  updated: 2026-10
  note: 只提供合规运营方法与测算口径；不提供刷单测评、黑帽排名、多账号规避、伪造认证、低报货值等违规方案，也不做税务筹划。
---

# 跨境运营手册

一句话：**先用规则筛掉不能做的品，再用数字算清能不能赚钱，最后才谈怎么放量。** 任何一环不成立，后面的运营技巧都是白忙。

## 什么时候用

| 该用 | 不该用 |
|---|---|
| 判断一个品/一个平台能不能做 | 要"保证爆单"式的收益承诺 |
| 算净利、保本价、保本 ACOS、备货量、回款周期 | 要刷单、测评换评、黑帽排名方案 |
| 排查"没流量 / 有流量不转化 / ACOS 高 / 被下架" | 要伪造认证、低报货值清关 |
| 做入驻、上新、月度复盘的执行清单 | 要代替本人注册账号、提交申诉、下单付款 |

## 目录结构

```
cross-border-ops/
├── SKILL.md
├── references/
│   ├── platform-rules.md          平台规则、入驻路径、处罚类型
│   ├── product-selection.md       选品逻辑、竞争与合规筛选
│   ├── listing-seo.md             Listing 结构、关键词分层、转化诊断
│   ├── ads.md                     广告结构、ACOS 五层排查
│   ├── logistics-warehousing.md   头程方式、仓配、备货与两头预案
│   ├── payments-tax.md            收款渠道、结汇边界、VAT/EPR/关税
│   ├── compliance-risk.md         认证、知产、账号风控、产品安全
│   └── metrics.md                 指标口径与诊断树、团队 KPI
├── scripts/
│   └── cbcalc.py                  净利 / 保本价 / 保本 ACOS / 备货 / 现金流
├── templates/
│   ├── product-eval.md            选品评估表
│   ├── launch-sop.md              90 天启动 SOP
│   └── monthly-review.html        月度复盘单页模板
└── examples/
    └── demo-conversations.md      典型问答示范
```

## 三层用法

**知识层**：先读对应 reference，再回答。不要在没读规则的情况下凭印象说平台政策。
**测算层**：任何涉及"赚多少 / 保本 / 备多少货 / 多久回款"的问题，先跑 `cbcalc.py`，不要口算。
**模板层**：涉及表单、SOP、复盘，直接套 `templates/`，比现场发挥更完整。

## 核心口径约定（回答时必须写明）

| 项目 | 口径 |
|---|---|
| 币种 | 一律写明站点币种（USD/EUR/GBP/JPY），人民币折算另起一行 |
| 售价 | 标"含税售价"还是"不含税售价"，EU 站点默认含 VAT |
| 净利 | **扣除**采购、头程、平台佣金、仓配、广告、支付、退货损失、税之后的单件净利 |
| 毛利率 | （售价 − 采购 − 头程 − 仓配）/ 售价，不含广告与平台佣金，避免与净利混淆 |
| 广告 | ACOS = 广告花费 / 广告销售额；TACOS = 广告花费 / 全店销售额 |
| 退货 | 用"退货率"与"报废率"两个参数，不要用一个模糊的损耗率糊过去 |
| 易变事实 | 标注"截至 YYYY-MM，执行前以后台/官方公告复核" |

## 分诊路由

| 用户问的是 | 先读 | 再跑 |
|---|---|---|
| 这个品能不能做 | `references/product-selection.md` | `cbcalc.py profit` |
| 到手赚多少 / 多少钱保本 | `references/product-selection.md` | `cbcalc.py profit --target-margin` |
| 广告能不能再烧 | `references/ads.md` | `cbcalc.py beacos` |
| 备多少货 / 会不会断货 | `references/logistics-warehousing.md` | `cbcalc.py reorder` |
| 钱多久回来 / 现金流够不够 | `references/payments-tax.md` | `cbcalc.py cash` |
| 被下架 / 被限流 / 绩效警告 | `references/platform-rules.md` + `compliance-risk.md` | — |
| 要交什么认证 / 要不要注册 VAT | `references/compliance-risk.md` + `payments-tax.md` | — |
| 没流量 / 不转化 / 排名掉了 | `references/listing-seo.md` | — |
| 团队怎么分 / 月度看什么 | `references/metrics.md` | — |

## 测算脚本

```bash
# 单件净利 + 保本售价 + 保本 ACOS（参数缺省会按参考区间代入并标"假设"）
python3 scripts/cbcalc.py profit --price 29.99 --cost 6.2 --freight 1.8 \
  --commission 0.15 --fulfillment 5.1 --ad-rate 0.12 --pay-rate 0.01 \
  --return-rate 0.08 --scrap-rate 0.7 --target-margin 0.15

# 反推：给定目标净利率，允许的广告占比上限（= 保本 ACOS 参考）
python3 scripts/cbcalc.py beacos --price 29.99 --cost 6.2 --freight 1.8 \
  --commission 0.15 --fulfillment 5.1 --pay-rate 0.01

# 备货：日销、补货总周期、安全库存、MOQ 与装箱数
python3 scripts/cbcalc.py reorder --daily-sales 18 --lead-days 45 \
  --safety-days 20 --moq 500 --carton 40

# 现金流：月销、结算周期、生产周期、在途天数、头程与货值
python3 scripts/cbcalc.py cash --monthly-revenue 60000 --cogs-rate 0.3 \
  --payout-days 14 --production-days 20 --transit-days 35 --ad-rate 0.12
```

加 `--json` 输出机器可读结果，便于二次加工。**所有假设都会打印在结果表头，回答时原样转述给用户。**

## 输出规范

1. **结论先行**：能不能做 / 赚不赚 / 够不够，第一句说完。
2. **表格承载数字**：项目 / 金额 / 占售价比例 / 口径说明；最后一行是净利。
3. **假设显式化**：缺参数时用区间默认值，但必须标 `假设`，并给敏感性（售价 ±10%、广告占比 ±5pt）。
4. **动作落到人**：每条建议带"动作 / 负责角色 / 时限 / 判断有效的指标 / 观察窗口"。
5. **止损线必备**：可行性与投放建议必须同时给出"什么情况下停"。

## 合规红线（一律不做）

- 刷单、测评换评论、诱导好评、黑科技排名、操纵评论
- 多账号关联规避、买卖账号、借用他人主体过审
- 伪造认证/检测报告、低报货值清关、拆分包裹规避关税
- 盗图、跟卖侵权、抄竞品专利外观
- 税务筹划与"零申报"设计建议（只讲注册义务与申报节奏）

遇到这类诉求：明确拒绝，说明真实后果（封店、扣押、补税+罚金、法律责任），并给合规替代路径。

## 参考来源

- Amazon Seller Central 政策与费用页（各站点）
- TikTok Shop 跨境/本地店商家规则中心
- Temu 商家中心（全托管/半托管规则）
- Shopee / AliExpress 卖家中心规则
- 欧盟税务与海关（VAT、IOSS、EPR）、美国 CBP 与 FDA/FCC/CPSC、英国 HMRC
- 行业口径参考：Marketplace Pulse、卖家之家、雨果跨境等公开数据（仅作区间参考，不作结论依据）
