"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
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

export function HoldingsTable({ rows, onReload }: { rows: Holding[]; onReload: () => void }) {
    return (
        <>
            <div className="flex items-baseline gap-4 mb-2">
                <span className="text-3xl font-bold">Holdings — all accounts</span>
                <span className="text-lg text-gray-300">{rows.length} stocks</span>
            </div>
            <p className="text-base text-gray-300 mb-6">
                Tap any stock for its RSI, MACD, trend and 52-week range.
            </p>

            <div className="flex flex-col gap-3">
                {rows.map((r, i) => (
                    <Row key={r.id ?? `${r.account_label}-${r.symbol}-${i}`} r={r} onReload={onReload} />
                ))}
            </div>

            <p className="mt-8 text-base text-gray-300 leading-relaxed max-w-5xl">
                Numbers only — no buy/sell recommendations, no automated trading. Flags are rule-based
                (near 52-week high, moved &gt;15% from cost, held &gt;1 year for the long-term tax rate)
                so you make the call.
            </p>
        </>
    );
}

function formatOwner(label: string | null) {
    if (!label) return "—";
    const name = label.split('@')[0].replace(/[0-9]/g, '');
    if (name.toLowerCase() === 'kiransamantd' || name.toLowerCase() === 'kiransamant') return 'Kiran';
    return name.charAt(0).toUpperCase() + name.slice(1);
}

export function Row({ r, onReload }: { r: Holding; onReload: () => void }) {
    const [open, setOpen] = useState(false);
    const bs = brokerStyle(r.broker);
    const rsi = rsiView(r.rsi_14);
    const macd = macdView(r.macd_hist);
    const trend = trendView(r.trend);
    const changeColor = plColor(r.gain_loss ?? r.gain_loss_pct ?? null);
    const markPct = rangePercent(r.last_price, r.week52_low, r.week52_high);

    return (
        <div className="glass-surface rounded-2xl border border-white/10 overflow-hidden">
            <button
                onClick={() => setOpen((v) => !v)}
                className="w-full grid items-center gap-4 px-5 py-4 text-left hover:bg-white/[0.04] transition-colors"
                style={{ gridTemplateColumns: "1fr auto auto auto auto auto" }}
            >
                <div className="flex flex-col gap-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xl font-bold font-outfit text-white tracking-tight">{r.symbol}</span>
                        <span className="text-xs font-bold text-gray-300 border border-white/20 rounded px-1.5 py-0.5 bg-white/5">{r.exchange}</span>
                        <span
                            className="inline-flex items-center gap-1.5 text-xs font-bold px-2.5 py-1 rounded-full whitespace-nowrap"
                            style={{ background: bs.bg, color: bs.color }}
                        >
                            {bs.label}
                        </span>
                    </div>
                    <span className="text-base text-gray-300">
                        {r.company_name ? `${r.company_name} · ` : ""}
                        {formatOwner(r.account_label)} · {r.quantity} shares · held {daysHeldLabel(r.days_held)}
                    </span>
                </div>

                <div className="text-right hidden sm:block">
                    <div className="text-xs font-semibold text-gray-300 mb-0.5">BUY</div>
                    <div className="text-lg font-semibold text-gray-200 tabular-nums whitespace-nowrap">{inrPrice(r.avg_buy_price)}</div>
                </div>

                <div className="text-right">
                    <div className="text-xs font-semibold text-gray-300 mb-0.5">NOW</div>
                    <div className="text-lg font-bold text-white tabular-nums whitespace-nowrap">{inrPrice(r.last_price)}</div>
                </div>

                <div className="text-right">
                    <div className="text-xs font-semibold text-gray-300 mb-0.5">GAIN / LOSS</div>
                    <div className="text-lg font-bold tabular-nums whitespace-nowrap" style={{ color: changeColor }}>
                        {signedInr(r.gain_loss)}
                        <span className="text-sm font-semibold ml-1">({pctLabel(r.gain_loss_pct)})</span>
                    </div>
                </div>

                {r.flags.length > 0 && (
                    <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-amber-400/15 text-amber-300 border border-amber-400/30 whitespace-nowrap">
                        {r.flags.length} to know
                    </span>
                )}

                <ChevronDown className={`w-5 h-5 text-gray-300 transition-transform ${open ? "rotate-180" : ""}`} />
            </button>

            {open && (
                <div className="border-t border-white/10 px-5 py-5 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
                    <div className="sm:hidden">
                        <div className="text-xs font-bold uppercase tracking-wide text-gray-300 mb-1.5">Buy price</div>
                        <div className="text-lg font-semibold text-gray-200 tabular-nums">{inrPrice(r.avg_buy_price)}</div>
                    </div>

                    <div>
                        <div className="text-xs font-bold uppercase tracking-wide text-gray-300 mb-1.5">RSI (momentum)</div>
                        {rsi ? (
                            <>
                                <span className="inline-block text-sm font-bold px-3 py-1.5 rounded-lg tabular-nums" style={{ background: rsi.bg, color: rsi.color }}>{rsi.text}</span>
                                <div className="text-base text-gray-300 mt-1.5">{rsi.gloss}</div>
                            </>
                        ) : (
                            <span className="text-base text-gray-400">Not enough data yet</span>
                        )}
                    </div>

                    <div>
                        <div className="text-xs font-bold uppercase tracking-wide text-gray-300 mb-1.5">MACD (trend strength)</div>
                        {macd ? (
                            <>
                                <span className="inline-block text-sm font-bold px-3 py-1.5 rounded-lg" style={{ background: macd.bg, color: macd.color }}>{macd.text}</span>
                                <div className="text-base text-gray-300 mt-1.5">{macd.gloss}</div>
                            </>
                        ) : (
                            <span className="text-base text-gray-400">Not enough data yet</span>
                        )}
                    </div>

                    <div>
                        <div className="text-xs font-bold uppercase tracking-wide text-gray-300 mb-1.5">Trend</div>
                        <span className="font-outfit font-bold text-lg" style={{ color: trend.color }}>{trend.label}</span>
                        <div className="text-base text-gray-300 mt-1">{trend.sub}</div>
                    </div>

                    <div className="sm:col-span-2 lg:col-span-1">
                        <div className="text-xs font-bold uppercase tracking-wide text-gray-300 mb-1.5">52-week range</div>
                        {markPct === null ? (
                            <span className="text-base text-gray-400">Not enough data yet</span>
                        ) : (
                            <>
                                <div className="flex justify-between text-sm text-gray-300 mb-2 tabular-nums font-medium">
                                    <span>{inrPrice(r.week52_low)}</span>
                                    <span>{inrPrice(r.week52_high)}</span>
                                </div>
                                <div className="relative h-2 rounded-full bg-white/10">
                                    <div
                                        className="absolute top-1/2 w-5 h-5 rounded-full border-[3px] border-[#0a0f1e] -translate-x-1/2 -translate-y-1/2"
                                        style={{ left: `${markPct}%`, background: changeColor }}
                                    />
                                </div>
                            </>
                        )}
                    </div>

                    {r.flags.length > 0 && (
                        <div className="sm:col-span-2 lg:col-span-4 flex flex-wrap gap-2">
                            {r.flags.map((f) => (
                                <span key={f.code} className="text-sm font-bold px-3 py-1.5 rounded-full bg-white/10 text-gray-200 border border-white/20">
                                    {f.text}
                                </span>
                            ))}
                        </div>
                    )}

                    <div className="sm:col-span-2 lg:col-span-4 border-t border-white/10 pt-4">
                        <HeldDateEditor r={r} onReload={onReload} />
                    </div>
                </div>
            )}
        </div>
    );
}

function HeldDateEditor({ r, onReload }: { r: Holding; onReload: () => void }) {
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
            <div className="flex items-center gap-3">
                <label className="text-base text-gray-200">Purchase date:</label>
                <input
                    type="date"
                    max={today()}
                    defaultValue={r.first_buy_date ?? ""}
                    onChange={(e) => e.target.value && save(e.target.value)}
                    className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-base text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                {saving && <span className="text-base text-gray-300 animate-pulse">Saving…</span>}
            </div>
        );
    }

    return (
        <button
            onClick={() => setEditing(true)}
            className="text-base text-indigo-300 hover:text-indigo-200 font-semibold underline underline-offset-2"
        >
            {r.first_buy_date ? `Purchase date: ${r.first_buy_date} — change` : "Set purchase date"}
        </button>
    );
}
