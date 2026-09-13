// Pure formatting + derivation helpers for the Holdings dashboard.
// No React, no fetch — kept separate so the mapping rules stay testable
// and the component file stays about layout.

export interface RawFlag {
    code: string;
    text: string;
}

export interface TrendDict {
    label: string;
    strength: number;
    direction: "up" | "down" | "flat";
}

export interface Holding {
    id: string;
    account_label: string | null;
    broker: string | null;
    symbol: string;
    exchange: string;
    company_name: string | null;
    sector: string | null;
    cap_tier: string | null;
    quantity: number;
    avg_buy_price: number;
    last_price: number | null;
    last_price_at: string | null;
    week52_high: number | null;
    week52_low: number | null;
    rsi_14: number | null;
    macd_hist: number | null;
    trend: TrendDict | null;
    gain_loss: number | null;
    gain_loss_pct: number | null;
    first_buy_date: string | null;
    days_held: number | null;
    flags: RawFlag[];
}

const POS = "#34d399";
const NEG = "#fb7185";
const FLAT = "#9ca3af";
const WARN = "#fbbf24";

export function plColor(n: number | null | undefined): string {
    if (n === null || n === undefined || n === 0) return FLAT;
    return n > 0 ? POS : NEG;
}

const inrGroup = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 });
const inrPrice2 = new Intl.NumberFormat("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

/** Whole-rupee money, e.g. "₹9,01,340" — minus sign kept for losses. */
export function inr(n: number | null | undefined): string {
    if (n === null || n === undefined) return "—";
    const sign = n < 0 ? "−" : "";
    return `${sign}₹${inrGroup.format(Math.abs(Math.round(n)))}`;
}

/** Two-decimal price, e.g. "₹3,850.00". */
export function inrPrice(n: number | null | undefined): string {
    if (n === null || n === undefined) return "—";
    return `₹${inrPrice2.format(n)}`;
}

/** "+₹58,740" / "−₹27,000" with an explicit + on gains. */
export function signedInr(n: number | null | undefined): string {
    if (n === null || n === undefined) return "—";
    return (n > 0 ? "+" : "") + inr(n);
}

export function pctLabel(n: number | null | undefined): string {
    if (n === null || n === undefined) return "—";
    return `${n > 0 ? "+" : ""}${n.toFixed(1)}%`;
}

export interface Summary {
    invested: number;
    currentValue: number;
    pnl: number;
    pnlPct: number | null;
    flaggedCount: number;
    total: number;
}

export function summarise(rows: Holding[]): Summary {
    let invested = 0;
    let currentValue = 0;
    let flaggedCount = 0;
    for (const r of rows) {
        const cost = r.avg_buy_price * r.quantity;
        invested += cost;
        currentValue += (r.last_price ?? r.avg_buy_price) * r.quantity;
        if (r.flags.length > 0) flaggedCount += 1;
    }
    const pnl = currentValue - invested;
    return {
        invested,
        currentValue,
        pnl,
        pnlPct: invested > 0 ? (pnl / invested) * 100 : null,
        flaggedCount,
        total: rows.length,
    };
}

export interface AccountGroup {
    label: string;
    broker: string | null;
    value: number;
}

export function groupAccounts(rows: Holding[]): AccountGroup[] {
    const byLabel = new Map<string, AccountGroup>();
    for (const r of rows) {
        const label = r.account_label ?? "Unlinked";
        const existing = byLabel.get(label);
        const add = (r.last_price ?? r.avg_buy_price) * r.quantity;
        if (existing) {
            byLabel.set(label, { ...existing, value: existing.value + add });
        } else {
            byLabel.set(label, { label, broker: r.broker, value: add });
        }
    }
    return Array.from(byLabel.values()).sort((a, b) => b.value - a.value);
}

export interface BrokerStyle {
    bg: string;
    color: string;
    label: string;
}

export function brokerStyle(broker: string | null): BrokerStyle {
    switch (broker) {
        case "zerodha":
            return { bg: "rgba(129,140,248,0.14)", color: "#a5b4fc", label: "Zerodha" };
        case "mstock":
            return { bg: "rgba(167,139,250,0.14)", color: "#c4b5fd", label: "mStock" };
        default:
            return { bg: "rgba(255,255,255,0.06)", color: "#9ca3af", label: broker ?? "—" };
    }
}

/** Marker position on the 52-week track, 0–100. null if range unknown. */
export function rangePercent(
    last: number | null,
    low: number | null,
    high: number | null,
): number | null {
    if (last === null || low === null || high === null || high <= low) return null;
    const pct = ((last - low) / (high - low)) * 100;
    return Math.max(0, Math.min(100, pct));
}

export interface Badge {
    text: string;
    gloss: string;
    color: string;
    bg: string;
}

export function rsiView(rsi: number | null): Badge | null {
    if (rsi === null) return null;
    const v = Math.round(rsi);
    const text = `RSI ${v}`;
    if (v >= 70) return { text, gloss: "Overbought", color: NEG, bg: "rgba(244,63,94,0.14)" };
    if (v >= 60) return { text, gloss: "Getting expensive", color: WARN, bg: "rgba(251,191,36,0.14)" };
    if (v <= 30) return { text, gloss: "Oversold — looks cheap", color: POS, bg: "rgba(52,211,153,0.14)" };
    if (v <= 40) return { text, gloss: "Weak", color: FLAT, bg: "rgba(255,255,255,0.06)" };
    return { text, gloss: "Neutral", color: FLAT, bg: "rgba(255,255,255,0.06)" };
}

export function macdView(hist: number | null): Badge | null {
    if (hist === null) return null;
    if (hist > 0.05) return { text: "Rising", gloss: "Momentum up", color: POS, bg: "rgba(52,211,153,0.14)" };
    if (hist < -0.05) return { text: "Falling", gloss: "Momentum down", color: NEG, bg: "rgba(244,63,94,0.14)" };
    return { text: "Flat", gloss: "Steady", color: FLAT, bg: "rgba(255,255,255,0.06)" };
}

export interface TrendView {
    label: string;
    sub: string;
    color: string;
    size: number;
    weight: number;
}

export function trendView(trend: TrendDict | null): TrendView {
    switch (trend?.label) {
        case "Very Bullish":
            return { label: trend.label, sub: "▲▲ strong up", color: "#10e8a0", size: 17, weight: 800 };
        case "Bullish":
            return { label: trend.label, sub: "▲ going up", color: POS, size: 14, weight: 700 };
        case "Bearish":
            return { label: trend.label, sub: "▼ going down", color: NEG, size: 14, weight: 700 };
        case "Very Bearish":
            return { label: trend.label, sub: "▼▼ strong down", color: "#f43f5e", size: 17, weight: 800 };
        case "Neutral":
            return { label: trend.label, sub: "● flat", color: FLAT, size: 12.5, weight: 600 };
        default:
            return { label: "No signal", sub: "not enough price history", color: FLAT, size: 12.5, weight: 600 };
    }
}

// ---- aggregations for the summary dashboard ----

export interface SliceDatum {
    name: string;
    value: number;
    pct: number;
}

function toSlices(totals: Map<string, number>): SliceDatum[] {
    const grand = Array.from(totals.values()).reduce((a, b) => a + b, 0);
    return Array.from(totals.entries())
        .map(([name, value]) => ({ name, value, pct: grand > 0 ? (value / grand) * 100 : 0 }))
        .sort((a, b) => b.value - a.value);
}

function investedOf(r: Holding): number {
    return r.avg_buy_price * r.quantity;
}

function returnsOf(r: Holding): number {
    return r.gain_loss ?? ((r.last_price ?? r.avg_buy_price) - r.avg_buy_price) * r.quantity;
}

export function bySector(rows: Holding[]): SliceDatum[] {
    const t = new Map<string, number>();
    for (const r of rows) {
        const k = r.sector ?? "Unclassified";
        t.set(k, (t.get(k) ?? 0) + investedOf(r));
    }
    return toSlices(t);
}

export function byCapTier(rows: Holding[]): SliceDatum[] {
    const t = new Map<string, number>();
    for (const r of rows) {
        const k = r.cap_tier ?? "Unclassified";
        t.set(k, (t.get(k) ?? 0) + investedOf(r));
    }
    return toSlices(t);
}

export interface RankedDatum {
    name: string;
    invested: number;
    returns: number;
}

export function topByInvestment(rows: Holding[], n = 5): RankedDatum[] {
    return rows
        .map((r) => ({ name: r.symbol, invested: investedOf(r), returns: returnsOf(r) }))
        .sort((a, b) => b.invested - a.invested)
        .slice(0, n);
}

export function topByReturns(rows: Holding[], n = 5): RankedDatum[] {
    return rows
        .map((r) => ({ name: r.symbol, invested: investedOf(r), returns: returnsOf(r) }))
        .sort((a, b) => b.returns - a.returns)
        .slice(0, n);
}

export const CAP_TIERS = ["Large", "Mid", "Small", "Penny"] as const;

export function daysHeldLabel(days: number | null): string {
    if (days === null) return "— set date";
    if (days < 0) return "—";
    return `${days} day${days === 1 ? "" : "s"}`;
}
