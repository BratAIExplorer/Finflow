"use client";

import { useState } from "react";
import {
    Holding,
    inrPrice,
    signedInr,
    pctLabel,
    plColor,
    brokerStyle,
    rangePercent,
    rsiView,
    macdView,
    trendView,
    daysHeldLabel,
} from "@/lib/holdingsFormat";
import { TOKEN_KEY } from "../LoginModal";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const token = () => (typeof window !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null);
const today = () => new Date().toISOString().slice(0, 10);

const COLS = ["Owner", "Broker", "Stock / Ticker", "Held", "Buy Price", "Now", "52-Week Range", "Gain / Loss", "RSI", "MACD", "Trend"];

export function HoldingsTable({ rows, onReload }: { rows: Holding[]; onReload: () => void }) {
    return (
        <>
            <div className="flex items-baseline gap-4 mb-6">
                <span className="text-3xl font-bold">Holdings — all accounts</span>
                <span className="text-lg text-gray-400">{rows.length} stocks</span>
            </div>

            <div className="glass-surface rounded-2xl overflow-auto h-[85vh] shadow-2xl">
                <table className="w-full border-collapse min-w-[1400px]">
                    <thead>
                        <tr>
                            {COLS.map((h) => (
                                <th
                                    key={h}
                                    className="sticky top-0 z-[1] text-left text-sm font-bold uppercase tracking-wider text-gray-400 px-5 py-4 bg-[#0d1220] whitespace-nowrap border-b border-white/10"
                                >
                                    {h}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {rows.map((r, i) => (
                            <Row key={r.id ?? `${r.account_label}-${r.symbol}-${i}`} r={r} onReload={onReload} />
                        ))}
                    </tbody>
                </table>
            </div>

            <p className="mt-7 text-sm text-gray-500 leading-relaxed max-w-5xl">
                Numbers only — no buy/sell recommendations, no automated trading. Flags are rule-based
                (near 52-week high, moved &gt;15% from cost, held &gt;1 year for the long-term tax rate)
                so you make the call. Brokers don&apos;t send the purchase date — set it in the{" "}
                <strong className="text-gray-300">Held</strong> column to switch on the days-held count and the tax flag.
            </p>
        </>
    );
}

function Row({ r, onReload }: { r: Holding; onReload: () => void }) {
    const bs = brokerStyle(r.broker);
    const rsi = rsiView(r.rsi_14);
    const macd = macdView(r.macd_hist);
    const trend = trendView(r.trend);
    const changeColor = plColor(r.gain_loss ?? r.gain_loss_pct ?? null);
    const markPct = rangePercent(r.last_price, r.week52_low, r.week52_high);
    const td = "px-5 py-4 border-b border-white/[0.06]";

    return (
        <tr className="hover:bg-white/[0.05] transition-colors">
            <td className={`${td} whitespace-nowrap font-semibold text-gray-300 text-lg`}>{r.account_label ?? "—"}</td>
            <td className={td}>
                <span
                    className="inline-flex items-center gap-2 text-sm font-bold px-3 py-1.5 rounded-full whitespace-nowrap shadow-sm"
                    style={{ background: bs.bg, color: bs.color }}
                >
                    <span className="w-2 h-2 rounded-full" style={{ background: bs.color }} />
                    {bs.label}
                </span>
            </td>
            <td className={td}>
                <div className="flex flex-col gap-1 min-w-[200px]">
                    <div className="flex items-center gap-2">
                        <span className="text-2xl font-bold font-outfit text-white tracking-tight">{r.symbol}</span>
                        <span className="text-xs font-bold text-gray-400 border border-white/20 rounded px-1.5 py-0.5 bg-white/5">{r.exchange}</span>
                    </div>
                    <span className="text-sm text-gray-400 truncate max-w-[220px]">
                        {r.company_name ? `${r.company_name} · ` : ""}{r.quantity} sh
                    </span>
                </div>
            </td>
            <td className={td}>
                <HeldCell r={r} onReload={onReload} />
            </td>
            <td className={`${td} tabular-nums text-xl whitespace-nowrap text-gray-300`}>{inrPrice(r.avg_buy_price)}</td>
            <td className={`${td} tabular-nums text-2xl font-bold text-white whitespace-nowrap`}>{inrPrice(r.last_price)}</td>
            <td className={td}>
                {markPct === null ? (
                    <span className="text-sm text-gray-600">—</span>
                ) : (
                    <div className="min-w-[180px]">
                        <div className="flex justify-between text-sm text-gray-400 mb-2 tabular-nums font-medium">
                            <span>{inrPrice(r.week52_low)}</span>
                            <span>{inrPrice(r.week52_high)}</span>
                        </div>
                        <div className="relative h-2 rounded-full bg-white/10 overflow-visible">
                            <div
                                className="absolute top-1/2 w-5 h-5 rounded-full border-[3px] border-[#0a0f1e] -translate-x-1/2 -translate-y-1/2 shadow-md"
                                style={{ left: `${markPct}%`, background: changeColor }}
                            />
                        </div>
                    </div>
                )}
            </td>
            <td className={td}>
                <div className="flex flex-col gap-0.5">
                    <span className="font-bold text-2xl tabular-nums tracking-tight" style={{ color: changeColor }}>{signedInr(r.gain_loss)}</span>
                    <span className="text-lg font-semibold" style={{ color: changeColor }}>{pctLabel(r.gain_loss_pct)}</span>
                </div>
            </td>
            <td className={td}>
                {rsi ? (
                    <>
                        <span className="inline-block text-sm font-bold px-3 py-1.5 rounded-lg tabular-nums shadow-sm" style={{ background: rsi.bg, color: rsi.color }}>{rsi.text}</span>
                        <div className="text-sm text-gray-400 mt-1.5">{rsi.gloss}</div>
                    </>
                ) : (
                    <span className="text-sm text-gray-600">—</span>
                )}
            </td>
            <td className={td}>
                {macd ? (
                    <>
                        <span className="inline-block text-sm font-bold px-3 py-1.5 rounded-lg shadow-sm" style={{ background: macd.bg, color: macd.color }}>{macd.text}</span>
                        <div className="text-sm text-gray-400 mt-1.5">{macd.gloss}</div>
                    </>
                ) : (
                    <span className="text-sm text-gray-600">—</span>
                )}
            </td>
            <td className={td}>
                <div className="flex flex-col gap-1.5 min-w-[160px]">
                    <span className="font-outfit leading-tight drop-shadow-sm" style={{ fontSize: "24px", fontWeight: trend.weight, color: trend.color }}>
                        {trend.label}
                    </span>
                    <span className="text-sm text-gray-400 font-medium">{trend.sub}</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                        {r.flags.map((f) => (
                            <span
                                key={f.code}
                                className="text-xs font-bold px-2.5 py-1 rounded-full bg-white/10 text-gray-300 border border-white/20 w-fit"
                            >
                                {f.text}
                            </span>
                        ))}
                    </div>
                </div>
            </td>
        </tr>
    );
}

function HeldCell({ r, onReload }: { r: Holding; onReload: () => void }) {
    const [editing, setEditing] = useState(false);
    const [saving, setSaving] = useState(false);

    const save = async (value: string | null) => {
        setSaving(true);
        try {
            await fetch(`${API}/holdings/positions/${r.id}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json", Authorization: `Bearer ${token()}` },
                body: JSON.stringify({ first_buy_date: value }),
            });
            setEditing(false);
            onReload();
        } finally {
            setSaving(false);
        }
    };

    if (editing) {
        return (
            <div className="flex items-center gap-2">
                <input
                    type="date"
                    max={today()}
                    defaultValue={r.first_buy_date ?? ""}
                    onChange={(e) => e.target.value && save(e.target.value)}
                    className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                {saving && <span className="text-sm text-gray-400 animate-pulse">…</span>}
            </div>
        );
    }

    return (
        <button
            onClick={() => setEditing(true)}
            className="flex flex-col items-start gap-1 group transition-colors"
            title={r.first_buy_date ? `Bought ${r.first_buy_date} — click to change` : "Set purchase date"}
        >
            <span className={`text-lg font-bold ${r.days_held === null ? "text-indigo-400 group-hover:text-indigo-300" : "text-gray-100 group-hover:text-white"}`}>
                {daysHeldLabel(r.days_held)}
            </span>
            {r.first_buy_date && <span className="text-sm text-gray-400">{r.first_buy_date}</span>}
        </button>
    );
}
