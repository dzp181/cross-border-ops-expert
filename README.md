# 跨境运营专家 · Cross-Border Operations Expert

> 仓库：<https://github.com/dzp181/cross-border-ops-expert>　|　版本：v1.0.0　|　许可：MIT

面向中国跨境卖家的运营顾问：先合规筛品，再算清到手利润，最后才谈放量。内置一套运营手册与本地测算脚本。

## 类型

Agent 型（单个 AI 专家）　|　行业分类：07-SalesCommerce 销售商务（电商）

## 这位专家解决什么

跨境电商最常见的问题不是"不会运营"，而是**在不成立的模型上努力**：算错了头程、忽略了退货、把广告当增长、货压在仓里变成现金黑洞。这个专家的顺序固定：

1. **合规闸** — 认证、类目、知识产权过不了，直接说别做
2. **竞争闸** — 评论壁垒、价格带、品牌集中度
3. **利润闸** — 净利率不达标就改模型，不靠运营硬推
4. **放量** — 前三条成立后才谈广告与排名

## 覆盖能力

| 领域 | 具体内容 |
|---|---|
| 平台 | Amazon、TikTok Shop、Temu（全托管/半托管）、Shopee、AliExpress、Shopify 独立站 |
| 选品 | 需求真实性、竞争密度、差异化六路径、首批测款与止损线 |
| 利润 | 单件净利、净利率、保本售价、保本 ACOS、敏感性分析 |
| Listing | 标题结构、五点写法、图片逻辑、关键词分层与埋词、差评归因 |
| 广告 | 广告结构模板、ACOS 五层排查、分阶段打法、观察窗口与否定纪律 |
| 物流 | 头程方式对比、备货模型、补货点、断货与滞销两头预案、清关单据 |
| 资金 | 收款路径对比、结汇合规边界、现金占用与回款周期 |
| 合规 | 认证矩阵、EPR/VAT、账号风控、POA 申诉框架、产品安全 |
| 体系 | 指标口径、诊断树、团队分工与 KPI、月度复盘框架 |

## 内置技能：`skills/cross-border-ops`

```
references/  platform-rules · product-selection · listing-seo · ads
             logistics-warehousing · payments-tax · compliance-risk · metrics
scripts/     cbcalc.py（仅标准库，Python 3.9+）
templates/   product-eval.md · launch-sop.md · monthly-review.html
examples/    demo-conversations.md
```

### 测算脚本

```bash
# 单件净利 + 保本售价 + 保本 ACOS + 敏感性
python3 scripts/cbcalc.py profit --price 29.99 --cost 6.2 --freight 1.8 \
  --commission 0.15 --fulfillment 5.1 --ad-rate 0.12 --return-rate 0.08 --target-margin 0.15

# 保本 ACOS 反推
python3 scripts/cbcalc.py beacos --price 29.99 --cost 6.2 --freight 1.8 \
  --commission 0.15 --fulfillment 5.1 --target-margin 0.15

# 备货量与补货点（对齐 MOQ 与装箱数）
python3 scripts/cbcalc.py reorder --daily-sales 18 --lead-days 45 \
  --safety-days 20 --moq 500 --carton 40 --current-stock 300

# 现金占用与回款周期
python3 scripts/cbcalc.py cash --monthly-revenue 60000 --cogs-rate 0.3 \
  --payout-days 14 --production-days 20 --transit-days 35 --available-cash 30000
```

缺参数时脚本会用参考区间代入，并在表头标出「假设」，便于如实转述；加 `--json` 输出机器可读结果。

## 使用示例

- 我准备上 Amazon 美国站，帮我判断这个品能不能做，顺便算清到手利润
- TikTok Shop 和 Temu 半托管，小团队先做哪个？给我一个 90 天启动方案
- 我的 ACOS 一直压不下来，帮我按广告结构逐层排查，并给具体调整动作

## 边界（明确不做）

刷单测评、黑帽排名、多账号关联规避、伪造认证、低报货值清关、盗图跟卖、税务筹划。遇到这类诉求会拒绝并说明真实风险（封店、扣押、补税罚金、法律责任）。

## 数据时效

平台佣金、仓储费、税率、免税额、认证清单等易变事实，回答中标注核实月份，执行前必须以后台或官方公告复核。参考文件中的数值均为区间参考，不作结论依据。

## 头像

`avatars/expert.png` 已由 ImageGen 生成。替换要求：PNG/JPG、512×512、≤500KB。

## 安装

把整个目录放进专家目录：

```
~/.workbuddy/plugins/marketplaces/my-experts/plugins/cross-border-ops-expert/
```

然后注册：

```bash
python3 <expert-manager>/scripts/register_expert.py <expert-dir>
```

## 打包

```bash
python3 <expert-manager>/scripts/package_expert.py <expert-dir>
```

## 许可

MIT
