#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cbcalc.py — 跨境运营测算器（仅标准库，Python 3.9+）

四个子命令：
  profit   单件净利 / 净利率 / 保本售价 / 保本 ACOS（含敏感性）
  beacos   反推允许的广告占比上限（= 保本 ACOS 参考）
  reorder  补货点 / 建议补货量（对齐 MOQ 与装箱数）
  cash     现金占用 / 回款周期 / 周转次数

所有"缺省值"都会在结果表头标为「假设」，便于向用户如实转述。
加 --json 输出机器可读结果。

用法示例：
  python3 cbcalc.py profit --price 29.99 --cost 6.2 --freight 1.8 \
      --commission 0.15 --fulfillment 5.1 --ad-rate 0.12 --return-rate 0.08
"""

import argparse
import json
import sys
import unicodedata

# 参考区间默认值（仅在没有真实数据时使用，使用时必须在回答中标注为假设）
DEFAULTS = {
    "commission": 0.15,     # 平台佣金（Amazon 多数类目 8%-15%，按 15% 保守）
    "fulfillment": 0.0,     # 仓配/配送费（按件固定金额）
    "ad_rate": 0.12,        # 广告花费占售价比例
    "pay_rate": 0.01,       # 支付/收款费率
    "return_rate": 0.08,    # 退货率
    "scrap_rate": 0.70,     # 退货报废率（退回后无法二次销售的占比）
    "return_ship": 0.0,     # 单件退货运费损失
}


# ---------- 输出工具 ----------

def dwidth(s):
    """计算字符串显示宽度（CJK 记 2）"""
    w = 0
    for ch in str(s):
        w += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return w


def pad(s, width, align="left"):
    s = str(s)
    gap = max(0, width - dwidth(s))
    if align == "right":
        return " " * gap + s
    return s + " " * gap


def table(headers, rows, aligns=None):
    """打印对齐表格"""
    aligns = aligns or ["left"] * len(headers)
    widths = [dwidth(h) for h in headers]
    for r in rows:
        for i, c in enumerate(r):
            widths[i] = max(widths[i], dwidth(c))
    sep = "  "
    line_h = sep.join(pad(h, widths[i]) for i, h in enumerate(headers))
    print(line_h)
    print("-" * dwidth(line_h))
    for r in rows:
        print(sep.join(pad(c, widths[i], aligns[i]) for i, c in enumerate(r)))


def money(v):
    return f"{v:,.2f}"


def pct(v):
    return f"{v * 100:.1f}%"


def assumed_note(assumed):
    if not assumed:
        return "参数：全部由用户提供"
    return "假设（用户未提供，按参考区间代入，请在回答中标注）：" + "、".join(assumed)


# ---------- 核心模型 ----------
# 记：P 售价，C 采购成本，F 头程，M 仓配，k 平台佣金率，p 支付费率，
#     a 广告占比，r 退货率，s 报废率，rs 单件退货损失
#
#   净利 = (1-r)·P·(1-k-p) - a·P - (C+F+M) + r·C·(1-s) - r·rs
#
# 说明：
#   1) 广告费按发出件全额计入（点击已花钱，退货不退广告费）
#   2) 退货件不计收入，货值按 (1-报废率) 回收残值
#   3) 头程与仓配对退货件视为沉没

def calc_profit(price, cost, freight, commission, fulfillment,
                ad_rate, pay_rate, return_rate, scrap_rate, return_ship):
    kept = 1.0 - return_rate
    revenue = kept * price * (1 - commission - pay_rate)
    ad_cost = ad_rate * price
    goods = cost + freight + fulfillment
    salvage = return_rate * cost * (1 - scrap_rate)
    return_loss = return_rate * return_ship
    net = revenue - ad_cost - goods + salvage - return_loss
    return {
        "kept_revenue": revenue,
        "ad_cost": ad_cost,
        "goods": goods,
        "salvage": salvage,
        "return_loss": return_loss,
        "net": net,
        "net_margin": net / price if price else 0.0,
    }


def calc_break_even_price(cost, freight, commission, fulfillment,
                          ad_rate, pay_rate, return_rate, scrap_rate, return_ship):
    kept = 1.0 - return_rate
    coeff = kept * (1 - commission - pay_rate) - ad_rate
    if coeff <= 0:
        return None
    rhs = (cost + freight + fulfillment) - return_rate * cost * (1 - scrap_rate) + return_rate * return_ship
    return rhs / coeff


def calc_be_acos(price, cost, freight, commission, fulfillment,
                 pay_rate, return_rate, scrap_rate, return_ship):
    kept = 1.0 - return_rate
    headroom = (kept * price * (1 - commission - pay_rate)
                - (cost + freight + fulfillment)
                + return_rate * cost * (1 - scrap_rate)
                - return_rate * return_ship)
    return headroom / price if price else 0.0


def collect(args, fields):
    """从 args 收集参数，缺失则用默认值并记录假设"""
    out, assumed = {}, []
    labels = {
        "commission": "平台佣金率", "fulfillment": "仓配费", "ad_rate": "广告占比",
        "pay_rate": "支付费率", "return_rate": "退货率", "scrap_rate": "退货报废率",
        "return_ship": "单件退货运费",
    }
    for f in fields:
        v = getattr(args, f.replace("-", "_"), None)
        if v is None:
            v = DEFAULTS[f]
            assumed.append(f"{labels.get(f, f)}={v}")
        out[f] = v
    return out, assumed


# ---------- 子命令 ----------

def cmd_profit(args):
    p, assumed = collect(args, ["commission", "fulfillment", "ad_rate",
                                "pay_rate", "return_rate", "scrap_rate", "return_ship"])
    r = calc_profit(args.price, args.cost, args.freight, p["commission"], p["fulfillment"],
                    p["ad_rate"], p["pay_rate"], p["return_rate"], p["scrap_rate"], p["return_ship"])
    be_price = calc_break_even_price(args.cost, args.freight, p["commission"], p["fulfillment"],
                                     p["ad_rate"], p["pay_rate"], p["return_rate"],
                                     p["scrap_rate"], p["return_ship"])
    be_acos = calc_be_acos(args.price, args.cost, args.freight, p["commission"], p["fulfillment"],
                           p["pay_rate"], p["return_rate"], p["scrap_rate"], p["return_ship"])

    price = args.price
    # 退货损失 = 退货件放弃的净收入 − 可回收残值 + 退货运费损失
    ret_cost = (p["return_rate"] * price * (1 - p["commission"] - p["pay_rate"])
                - r["salvage"] + r["return_loss"])
    rows = [
        ("售价", money(price), "100.0%", "含税/不含税需自行确认"),
        ("采购成本", money(args.cost), pct(args.cost / price), "含包装"),
        ("头程", money(args.freight), pct(args.freight / price), "单件摊分"),
        ("仓配/配送", money(p["fulfillment"]), pct(p["fulfillment"] / price), "单件固定"),
        ("平台佣金", money(price * p["commission"]), pct(p["commission"]), "按售价比例"),
        ("支付/收款", money(price * p["pay_rate"]), pct(p["pay_rate"]), "按售价比例"),
        ("广告", money(r["ad_cost"]), pct(p["ad_rate"]), "按发出件全额计"),
        ("退货损失", money(ret_cost), pct(ret_cost / price),
         f"退货率 {pct(p['return_rate'])}，报废率 {pct(p['scrap_rate'])}，含残值回收"),
        ("净利润", money(r["net"]), pct(r["net_margin"]), "扣完全部费用"),
    ]

    print("=" * 76)
    print("单件净利测算")
    print(assumed_note(assumed))
    print("=" * 76)
    table(["项目", "金额", "占售价", "口径"], rows,
          ["left", "right", "right", "left"])
    print("-" * 76)
    print(f"单件净利：{money(r['net'])}   净利率：{pct(r['net_margin'])}")
    print(f"保本售价：{money(be_price) if be_price else '无法保本（成本结构已超过售价上限）'}")
    print(f"保本 ACOS（可承受广告占比）：{pct(be_acos)}")
    if args.target_margin is not None:
        allow = be_acos - args.target_margin
        print(f"目标净利率 {pct(args.target_margin)} → 允许广告占比上限：{pct(allow)}"
              f"（当前设定 {pct(p['ad_rate'])}，{'达标' if p['ad_rate'] <= allow else '超出'}）")
    print("-" * 76)
    print("敏感性（广告占比与售价变动对净利率的影响）")
    srows = []
    for ad_delta in (-0.05, 0.0, 0.05):
        row = [f"广告占比 {pct(p['ad_rate'] + ad_delta)}"]
        for price_mult in (0.9, 1.0, 1.1):
            rr = calc_profit(price * price_mult, args.cost, args.freight, p["commission"],
                             p["fulfillment"], max(0.0, p["ad_rate"] + ad_delta), p["pay_rate"],
                             p["return_rate"], p["scrap_rate"], p["return_ship"])
            row.append(pct(rr["net_margin"]))
        srows.append(row)
    table(["场景", "售价 -10%", "售价持平", "售价 +10%"], srows,
          ["left", "right", "right", "right"])
    print("-" * 76)
    if r["net_margin"] < 0.10:
        print("判定：净利率低于 10%，模型不成立。先改成本结构（采购/头程/规格），不要靠运营硬推。")
    elif r["net_margin"] < 0.15:
        print("判定：净利率 10%-15%，偏薄。可用但抗风险差（一次退货潮或一轮涨价就会转亏）。")
    elif r["net_margin"] < 0.25:
        print("判定：净利率 15%-25%，标品可做。给广告与促销留了空间。")
    else:
        print("判定：净利率 ≥ 25%，健康。优先把利润投在库存周转与词排名上，而不是降价。")

    if args.json:
        print(json.dumps({
            "net_per_unit": round(r["net"], 4),
            "net_margin": round(r["net_margin"], 4),
            "break_even_price": round(be_price, 4) if be_price else None,
            "break_even_acos": round(be_acos, 4),
            "assumptions": assumed,
        }, ensure_ascii=False))


def cmd_beacos(args):
    p, assumed = collect(args, ["fulfillment", "pay_rate", "return_rate",
                                "scrap_rate", "return_ship"])
    be = calc_be_acos(args.price, args.cost, args.freight, args.commission, p["fulfillment"],
                      p["pay_rate"], p["return_rate"], p["scrap_rate"], p["return_ship"])
    print("=" * 60)
    print("保本 ACOS 反推")
    print(assumed_note(assumed))
    print("=" * 60)
    rows = [
        ("售价", money(args.price), "—"),
        ("固定成本（采购+头程+仓配）", money(args.cost + args.freight + p["fulfillment"]), "—"),
        ("平台佣金+支付", money(args.price * (args.commission + p["pay_rate"])), pct(args.commission + p["pay_rate"])),
        ("保本 ACOS", pct(be), "广告花到这一比例即不赚不亏"),
    ]
    table(["项目", "金额/比例", "说明"], rows, ["left", "right", "left"])
    print("-" * 60)
    if args.target_margin is not None:
        print(f"目标净利率 {pct(args.target_margin)} → 广告占比上限 {pct(be - args.target_margin)}")
    print(f"参考：广告占比每多 1 个百分点，净利率下降 1 个百分点（按售价口径）")
    if args.json:
        print(json.dumps({"break_even_acos": round(be, 4), "assumptions": assumed}, ensure_ascii=False))


def cmd_reorder(args):
    lead = args.lead_days
    cover = args.cover_days if args.cover_days else lead + args.safety_days
    rop = args.daily_sales * (lead + args.safety_days)
    target = args.daily_sales * (lead + cover)
    raw = target - args.current_stock - args.in_transit
    raw_positive = max(0.0, raw)
    # 对齐装箱数，再保证不低于 MOQ
    if args.carton > 0:
        boxes = -(-raw_positive // args.carton)
        qty = boxes * args.carton
    else:
        qty = raw_positive
    if qty < args.moq:
        qty = args.moq
    days_of_stock = (args.current_stock + args.in_transit) / args.daily_sales if args.daily_sales else 0

    print("=" * 66)
    print("备货测算")
    print("=" * 66)
    rows = [
        ("日均销量", f"{args.daily_sales:,.1f}", "近 30 天销量÷30，去掉异常大单"),
        ("补货总周期", f"{lead:.0f} 天", "生产 + 头程 + 入仓上架 + 缓冲"),
        ("安全库存天数", f"{args.safety_days:.0f} 天", "按销量波动率取 15-30 天"),
        ("补货点", f"{rop:,.0f} 件", "库存降到此数即下单"),
        ("当前可用库存", f"{args.current_stock:,.0f} 件", f"约 {days_of_stock:.0f} 天"),
        ("在途", f"{args.in_transit:,.0f} 件", "已下单未入仓"),
        ("理论缺口", f"{raw_positive:,.0f} 件", "目标库存 − 现有 − 在途"),
        ("建议补货量", f"{qty:,.0f} 件", f"对齐装箱 {args.carton:,.0f} 件、MOQ {args.moq:,.0f} 件"),
    ]
    table(["项目", "数值", "说明"], rows, ["left", "right", "left"])
    print("-" * 66)
    if days_of_stock < lead:
        print(f"⚠️ 风险：现有+在途仅够 {days_of_stock:.0f} 天，短于补货周期 {lead:.0f} 天 —— 会断货，"
              f"立即下补货单并评估空运/快递救急（建议补 20%-30%）。")
    elif days_of_stock < lead + args.safety_days:
        print(f"⚠️ 提示：库存 {days_of_stock:.0f} 天已接近补货点，本周内下单。")
    else:
        print(f"✅ 库存 {days_of_stock:.0f} 天，高于补货周期+安全库存，按节奏补货即可。")
    if args.json:
        print(json.dumps({"reorder_point": round(rop, 2), "suggested_qty": qty,
                          "days_of_stock": round(days_of_stock, 1)}, ensure_ascii=False))


def cmd_cash(args):
    daily_rev = args.monthly_revenue / 30.0
    daily_cogs = daily_rev * args.cogs_rate
    stock = daily_cogs * args.inventory_days
    transit = daily_cogs * args.transit_days
    pending = daily_rev * args.payout_days
    ad_prepay = args.monthly_revenue * args.ad_rate
    total = stock + transit + pending + ad_prepay
    cycle = args.production_days + args.transit_days + args.inventory_days / 2.0 + args.payout_days
    turns = 365.0 / cycle if cycle else 0

    print("=" * 72)
    print("现金占用与回款周期")
    print("=" * 72)
    rows = [
        ("月销售额", money(args.monthly_revenue), "站点币种"),
        ("月货值（采购成本）", money(args.monthly_revenue * args.cogs_rate), f"占售价比 {pct(args.cogs_rate)}"),
        ("在库库存占用", money(stock), f"{args.inventory_days:.0f} 天库存"),
        ("在途库存占用", money(transit), f"{args.transit_days:.0f} 天头程"),
        ("平台待结算", money(pending), f"{args.payout_days:.0f} 天结算周期"),
        ("广告当月投入", money(ad_prepay), f"占售价比 {pct(args.ad_rate)}"),
        ("合计现金占用", money(total), "不含押金、认证、拍摄等一次性投入"),
    ]
    table(["项目", "金额", "说明"], rows, ["left", "right", "left"])
    print("-" * 72)
    print(f"回款周期（付货款 → 收到钱）：约 {cycle:.0f} 天"
          f"（生产 {args.production_days:.0f} + 头程 {args.transit_days:.0f} + "
          f"平均在库 {args.inventory_days / 2:.0f} + 结算 {args.payout_days:.0f}）")
    print(f"年化资金周转：约 {turns:.1f} 次")
    if args.available_cash:
        gap = total - args.available_cash
        if gap > 0:
            print(f"⚠️ 资金缺口：约 {money(gap)}。要么压月销，要么延长账期/提高周转，不要靠借贷填库存。")
        else:
            print(f"✅ 现金覆盖充足，冗余 {money(-gap)}（建议冗余不低于月销的 20%）。")
    print("-" * 72)
    print("纪律：备货预算不超过可动用资金的 60%；旺季前 3 个月开始备现金。")
    if args.json:
        print(json.dumps({"cash_locked": round(total, 2), "cycle_days": round(cycle, 1),
                          "turns_per_year": round(turns, 2)}, ensure_ascii=False))


# ---------- 入口 ----------

def build_parser():
    ap = argparse.ArgumentParser(description="跨境运营测算器：净利 / 保本价 / 保本ACOS / 备货 / 现金流")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("profit", help="单件净利测算")
    p1.add_argument("--price", type=float, required=True, help="售价")
    p1.add_argument("--cost", type=float, required=True, help="采购成本（含包装）")
    p1.add_argument("--freight", type=float, default=0.0, help="单件头程")
    p1.add_argument("--commission", type=float, help="平台佣金率，如 0.15")
    p1.add_argument("--fulfillment", type=float, help="单件仓配/配送费")
    p1.add_argument("--ad-rate", dest="ad_rate", type=float, help="广告花费占售价比例")
    p1.add_argument("--pay-rate", dest="pay_rate", type=float, help="支付/收款费率")
    p1.add_argument("--return-rate", dest="return_rate", type=float, help="退货率")
    p1.add_argument("--scrap-rate", dest="scrap_rate", type=float, help="退货报废率")
    p1.add_argument("--return-ship", dest="return_ship", type=float, help="单件退货运费损失")
    p1.add_argument("--target-margin", dest="target_margin", type=float, help="目标净利率，如 0.15")
    p1.add_argument("--json", action="store_true")
    p1.set_defaults(func=cmd_profit)

    p2 = sub.add_parser("beacos", help="反推保本 ACOS")
    p2.add_argument("--price", type=float, required=True)
    p2.add_argument("--cost", type=float, required=True)
    p2.add_argument("--freight", type=float, default=0.0)
    p2.add_argument("--commission", type=float, required=True)
    p2.add_argument("--fulfillment", type=float)
    p2.add_argument("--pay-rate", dest="pay_rate", type=float)
    p2.add_argument("--return-rate", dest="return_rate", type=float)
    p2.add_argument("--scrap-rate", dest="scrap_rate", type=float)
    p2.add_argument("--return-ship", dest="return_ship", type=float)
    p2.add_argument("--target-margin", dest="target_margin", type=float)
    p2.add_argument("--json", action="store_true")
    p2.set_defaults(func=cmd_beacos)

    p3 = sub.add_parser("reorder", help="备货量与补货点")
    p3.add_argument("--daily-sales", dest="daily_sales", type=float, required=True)
    p3.add_argument("--lead-days", dest="lead_days", type=float, required=True, help="补货总周期")
    p3.add_argument("--safety-days", dest="safety_days", type=float, default=20.0)
    p3.add_argument("--cover-days", dest="cover_days", type=float, default=0.0, help="目标覆盖天数，默认=周期+安全")
    p3.add_argument("--moq", type=float, default=0.0)
    p3.add_argument("--carton", type=float, default=0.0, help="装箱数")
    p3.add_argument("--current-stock", dest="current_stock", type=float, default=0.0)
    p3.add_argument("--in-transit", dest="in_transit", type=float, default=0.0)
    p3.add_argument("--json", action="store_true")
    p3.set_defaults(func=cmd_reorder)

    p4 = sub.add_parser("cash", help="现金占用与回款周期")
    p4.add_argument("--monthly-revenue", dest="monthly_revenue", type=float, required=True)
    p4.add_argument("--cogs-rate", dest="cogs_rate", type=float, default=0.30, help="货值占售价比例")
    p4.add_argument("--payout-days", dest="payout_days", type=float, default=14.0)
    p4.add_argument("--production-days", dest="production_days", type=float, default=20.0)
    p4.add_argument("--transit-days", dest="transit_days", type=float, default=35.0)
    p4.add_argument("--inventory-days", dest="inventory_days", type=float, default=60.0)
    p4.add_argument("--ad-rate", dest="ad_rate", type=float, default=0.12)
    p4.add_argument("--available-cash", dest="available_cash", type=float, default=0.0)
    p4.add_argument("--json", action="store_true")
    p4.set_defaults(func=cmd_cash)

    return ap


def main():
    ap = build_parser()
    args = ap.parse_args()
    try:
        args.func(args)
    except BrokenPipeError:
        sys.exit(0)


if __name__ == "__main__":
    main()
