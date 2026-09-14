"use client";

import React, { useEffect, useState } from "react";
import { Loader2, RefreshCw, Plus, X } from "lucide-react";
import { TOKEN_KEY } from "@/components/LoginModal";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const getToken = () => (typeof window !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null);

interface StockItem {
    symbol: string;
    name: string;
    price: string;
    chg: string;
    dir: "up" | "down";
    rsi: number | string;
    rsiW: [string, "good" | "bad" | "mid"];
    macdW: [string, "good" | "bad" | "mid"];
    verdict: {
        key: "v-vbull" | "v-bull" | "v-neut" | "v-bear" | "v-vbear";
        big: string;
        sub: string;
    };
    held: boolean;
}

interface NewsItem {
    id: string;
    symbol: string;
    name: string;
    head: string;
    src: string;
    time: string;
    cls: "pos" | "neg" | "neu";
    important: boolean;
}

interface BoardSnapshot {
    ts: string;
    stocks: StockItem[];
    news: NewsItem[];
    prices_ok: boolean;
    news_ok: boolean;
    out_dir: string;
}

export function MarketBoardPanel() {
    const [snap, setSnap] = useState<BoardSnapshot | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Form states
    const [symbol, setSymbol] = useState("");
    const [name, setName] = useState("");
    const [actionLoading, setActionLoading] = useState(false);

    const loadBoard = async () => {
        try {
            const res = await fetch(`${API}/board/`, {
                headers: { Authorization: `Bearer ${getToken()}` },
            });
            if (!res.ok) {
                const detail = (await res.json().catch(() => ({})))?.detail;
                throw new Error(detail || `Failed to load board (${res.status})`);
            }
            const data = await res.json();
            setSnap(data);
        } catch (e) {
            setError((e as Error).message);
        } finally {
            setLoading(false);
        }
    };

    const handleRefresh = async () => {
        setRefreshing(true);
        try {
            const res = await fetch(`${API}/board/refresh`, {
                method: "POST",
                headers: { Authorization: `Bearer ${getToken()}` },
            });
            if (!res.ok) throw new Error("Refresh failed");
            const data = await res.json();
            setSnap(data);
        } catch (e) {
            setError((e as Error).message);
        } finally {
            setRefreshing(false);
        }
    };

    const handleAdd = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!symbol.trim()) return;
        setActionLoading(true);
        try {
            const res = await fetch(`${API}/board/add`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${getToken()}`,
                },
                body: JSON.stringify({ symbol: symbol.trim(), name: name.trim() }),
            });
            if (!res.ok) throw new Error("Failed to add stock");
            const data = await res.json();
            setSnap(data);
            setSymbol("");
            setName("");
        } catch (e) {
            alert((e as Error).message);
        } finally {
            setActionLoading(false);
        }
    };

    const handleRemove = async (sym: string) => {
        setActionLoading(true);
        try {
            const res = await fetch(`${API}/board/remove`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${getToken()}`,
                },
                body: JSON.stringify({ symbol: sym }),
            });
            if (!res.ok) throw new Error("Failed to remove stock");
            const data = await res.json();
            setSnap(data);
        } catch (e) {
            alert((e as Error).message);
        } finally {
            setActionLoading(false);
        }
    };

    useEffect(() => {
        loadBoard();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center gap-4 py-20 text-slate-300">
                <Loader2 className="w-8 h-8 animate-spin text-indigo-400" />
                <span className="text-2xl font-medium">Loading Deepak&apos;s Market Board…</span>
            </div>
        );
    }

    if (error && !snap) {
        return (
            <div className="p-8 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-300">
                <p className="font-bold text-2xl mb-3">Could not load Market Board</p>
                <p className="text-lg opacity-90">{error}</p>
                <button
                    onClick={loadBoard}
                    className="mt-6 px-6 py-3 rounded-lg text-lg font-semibold bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 transition-colors"
                >
                    Retry
                </button>
            </div>
        );
    }

    if (!snap) return null;

    return (
        <div className="rounded-3xl bg-[#FBF7EF] text-[#1A1A1A] p-6 md:p-10 shadow-2xl border border-[#E7DFCF] font-sans selection:bg-amber-200">
            {/* Top Bar */}
            <header className="flex flex-wrap items-end justify-between gap-4 pb-6 border-b-2 border-[#1A1A1A]">
                <div>
                    <h1 className="text-5xl md:text-6xl font-serif font-bold tracking-tight text-[#1A1A1A]">
                        Deepak&apos;s Market Board
                    </h1>
                </div>
                <div className="text-3xl md:text-4xl font-bold font-mono tracking-tight text-[#1A1A1A]">
                    {snap.ts}
                </div>

                <div className="w-full flex flex-wrap items-center gap-5 md:gap-8 text-lg md:text-xl text-[#5B5750] pt-3">
                    <button
                        onClick={handleRefresh}
                        disabled={refreshing || actionLoading}
                        className="bg-[#123B6D] hover:bg-[#0e2c52] text-white font-bold text-lg px-7 py-3 rounded-xl shadow-md transition-all active:translate-y-0.5 flex items-center gap-2 cursor-pointer disabled:opacity-50"
                    >
                        {refreshing ? <Loader2 className="w-6 h-6 animate-spin" /> : <RefreshCw className="w-6 h-6" />}
                        Refresh now
                    </button>

                    <span className="font-medium">Last updated {snap.ts}</span>

                    <span className="inline-flex items-center gap-2 font-semibold text-lg">
                        <span
                            className={`w-4 h-4 rounded-full ${
                                snap.prices_ok ? "bg-[#00A651]" : "bg-[#E4002B]"
                            }`}
                        />
                        Prices {snap.prices_ok ? "working" : "problem"}
                    </span>

                    <span className="inline-flex items-center gap-2 font-semibold text-lg">
                        <span
                            className={`w-4 h-4 rounded-full ${
                                snap.news_ok ? "bg-[#00A651]" : "bg-[#E4002B]"
                            }`}
                        />
                        News {snap.news_ok ? "working" : "problem"}
                    </span>

                    {snap.out_dir && (
                        <span className="truncate max-w-md font-medium">Files saved to {snap.out_dir}</span>
                    )}
                </div>
            </header>

            {/* Layout Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-[1.35fr_1fr] gap-8 mt-8">
                {/* Left Column: Stocks */}
                <section>
                    <h2 className="text-4xl md:text-5xl font-serif font-bold mb-3 text-[#1A1A1A]">
                        My stocks — how they look today
                    </h2>
                    <p className="text-lg md:text-xl text-[#5B5750] mb-8 font-medium">
                        Big word = the direction. Green going up, red going down.
                    </p>

                    <div className="space-y-5">
                        {snap.stocks.length === 0 ? (
                            <p className="p-8 bg-white rounded-2xl border-2 border-[#E7DFCF] text-[#5B5750] text-xl font-medium">
                                No stocks yet — add some on the right.
                            </p>
                        ) : (
                            snap.stocks.map((s) => {
                                const isBull = s.verdict.key === "v-vbull" || s.verdict.key === "v-bull";
                                const isBear = s.verdict.key === "v-vbear" || s.verdict.key === "v-bear";
                                const verdictBg = isBull
                                    ? "bg-[#E4F6EC] text-[#00753A]"
                                    : isBear
                                    ? "bg-[#FBE4E8] text-[#B4001F]"
                                    : "bg-[#F1EAD9] text-[#6b6355]";

                                return (
                                    <article
                                        key={s.symbol}
                                        className="bg-white border-2 border-[#E7DFCF] rounded-2xl p-6 md:p-7 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-5"
                                    >
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-3 flex-wrap mb-2">
                                                <span className="text-3xl font-serif font-bold text-[#1A1A1A]">
                                                    {s.name}
                                                </span>
                                                <span className="text-sm font-extrabold uppercase tracking-wider px-3 py-1.5 rounded-md bg-[#EDEAE2] text-[#6b6355] border border-[#E7DFCF]">
                                                    Watching only
                                                </span>
                                            </div>

                                            <div className="text-lg font-semibold tracking-wider text-[#5B5750] uppercase mb-2">
                                                {s.symbol}
                                            </div>

                                            <div className="flex items-baseline gap-4 mb-3 font-mono">
                                                <span className="text-3xl font-bold text-[#1A1A1A]">{s.price}</span>
                                                <span
                                                    className={`text-2xl font-bold ${
                                                        s.dir === "up" ? "text-[#00A651]" : "text-[#E4002B]"
                                                    }`}
                                                >
                                                    {s.chg}
                                                </span>
                                            </div>

                                            <div className="text-lg text-[#5B5750] font-medium mb-4">
                                                Not bought — on the list to watch{" "}
                                                <em className="text-slate-400">(holdings come in Phase 1)</em>
                                            </div>

                                            <div className="flex flex-wrap gap-3">
                                                <span className="inline-flex items-center gap-2 bg-[#FBF7EF] border border-[#E7DFCF] rounded-lg px-4 py-2 text-base font-semibold text-[#1A1A1A]">
                                                    RSI <b className="font-mono text-lg">{s.rsi}</b>{" "}
                                                    <span
                                                        className={
                                                            s.rsiW[1] === "good"
                                                                ? "text-[#00753A] font-bold"
                                                                : s.rsiW[1] === "bad"
                                                                ? "text-[#B4001F] font-bold"
                                                                : "text-[#6b6355]"
                                                        }
                                                    >
                                                        {s.rsiW[0]}
                                                    </span>
                                                </span>

                                                <span className="inline-flex items-center gap-2 bg-[#FBF7EF] border border-[#E7DFCF] rounded-lg px-4 py-2 text-base font-semibold text-[#1A1A1A]">
                                                    MACD{" "}
                                                    <span
                                                        className={
                                                            s.macdW[1] === "good"
                                                                ? "text-[#00753A] font-bold"
                                                                : s.macdW[1] === "bad"
                                                                ? "text-[#B4001F] font-bold"
                                                                : "text-[#6b6355]"
                                                        }
                                                    >
                                                        {s.macdW[0]}
                                                    </span>
                                                </span>
                                            </div>
                                        </div>

                                        {/* Big Verdict badge */}
                                        <div
                                            className={`shrink-0 text-center md:text-right p-5 rounded-xl min-w-[160px] font-serif ${verdictBg}`}
                                        >
                                            <div className="text-4xl md:text-5xl font-bold leading-none">
                                                {s.verdict.big}
                                            </div>
                                            <small className="block font-sans text-sm font-semibold opacity-80 mt-2">
                                                {s.verdict.sub}
                                            </small>
                                        </div>
                                    </article>
                                );
                            })
                        )}
                    </div>
                </section>

                {/* Right Column: Add/Remove + News */}
                <section>
                    {/* Add / Remove Box */}
                    <div className="bg-white border-2 border-dashed border-[#123B6D] rounded-2xl p-8 mb-8">
                        <h2 className="text-3xl md:text-4xl font-serif font-bold text-[#1A1A1A] mb-2">
                            My stocks — add or remove
                        </h2>
                        <p className="text-lg text-[#5B5750] mb-6 font-medium">
                            Type an NSE symbol and a name, press <strong>Add</strong>. Red ✕ removes.
                        </p>

                        <form onSubmit={handleAdd} className="flex flex-wrap gap-3 mb-6">
                            <input
                                value={symbol}
                                onChange={(e) => setSymbol(e.target.value)}
                                placeholder="Symbol e.g. TATAPOWER"
                                aria-label="NSE symbol"
                                required
                                className="flex-1 min-w-[140px] bg-[#FBF7EF] border-2 border-[#E7DFCF] rounded-xl px-5 py-3 text-lg font-medium text-[#1A1A1A] focus:outline-none focus:border-[#123B6D]"
                            />
                            <input
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="Name e.g. Tata Power"
                                aria-label="Company name"
                                className="flex-1 min-w-[140px] bg-[#FBF7EF] border-2 border-[#E7DFCF] rounded-xl px-5 py-3 text-lg font-medium text-[#1A1A1A] focus:outline-none focus:border-[#123B6D]"
                            />
                            <button
                                type="submit"
                                disabled={actionLoading}
                                className="bg-[#00A651] hover:bg-[#008f45] text-white font-bold text-lg px-7 py-3 rounded-xl cursor-pointer shadow-sm transition-all disabled:opacity-50"
                            >
                                Add
                            </button>
                        </form>

                        <div className="text-sm font-extrabold uppercase tracking-wider text-[#5B5750] mb-4">
                            Your stocks — tap the red ✕ to remove
                        </div>

                        <div className="flex flex-wrap gap-3">
                            {snap.stocks.map((s) => (
                                <span
                                    key={s.symbol}
                                    className="inline-flex items-center gap-2 bg-[#FBF7EF] border-2 border-[#E7DFCF] rounded-full pl-4 pr-2 py-1.5 text-base font-bold text-[#1A1A1A]"
                                >
                                    {s.symbol}
                                    <button
                                        onClick={() => handleRemove(s.symbol)}
                                        disabled={actionLoading}
                                        aria-label={`Remove ${s.symbol}`}
                                        className="w-7 h-7 rounded-full bg-[#E4002B] hover:bg-[#c90025] text-white flex items-center justify-center text-sm font-bold cursor-pointer transition-colors"
                                    >
                                        ✕
                                    </button>
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* Latest Company News */}
                    <div className="bg-white border-2 border-[#E7DFCF] rounded-2xl shadow-sm overflow-hidden">
                        <div className="p-8 border-b border-[#E7DFCF]">
                            <h2 className="text-3xl md:text-4xl font-serif font-bold text-[#1A1A1A] mb-2">
                                Latest company news
                            </h2>
                            <p className="text-lg text-[#5B5750] font-medium">
                                Newest first. A red{" "}
                                <span className="bg-[#E4002B] text-white font-bold text-sm px-2 py-1 rounded">
                                    IMPORTANT
                                </span>{" "}
                                tag means a price-sensitive word (order, results, pledge...).
                            </p>
                        </div>

                        <div className="divide-y divide-[#E7DFCF] max-h-[700px] overflow-y-auto">
                            {snap.news.length === 0 ? (
                                <div className="p-8 text-lg text-[#5B5750] font-medium">
                                    No news pulled yet. It refreshes about once an hour.
                                </div>
                            ) : (
                                snap.news.map((n) => {
                                    const borderClass =
                                        n.cls === "pos"
                                            ? "border-l-8 border-[#00A651]"
                                            : n.cls === "neg"
                                            ? "border-l-8 border-[#E4002B]"
                                            : "border-l-8 border-[#F59E00]";
                                    return (
                                        <div key={n.id} className={`p-5 md:p-6 ${borderClass} hover:bg-slate-50 transition-colors`}>
                                            <div className="text-lg md:text-xl font-semibold text-[#1A1A1A] leading-snug mb-3">
                                                {n.head}
                                            </div>
                                            <div className="flex flex-wrap items-center gap-3 text-sm md:text-base text-[#5B5750]">
                                                {n.important && (
                                                    <span className="bg-[#E4002B] text-white font-bold px-3 py-1 rounded text-sm uppercase tracking-wider">
                                                        IMPORTANT
                                                    </span>
                                                )}
                                                <span className="font-bold text-[#123B6D]">{n.symbol}</span>
                                                <span>{n.src}</span>
                                                <span>{n.time}</span>
                                            </div>
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </div>
                </section>
            </div>

            {/* Sources Table */}
            <section className="mt-12 bg-white border-2 border-[#E7DFCF] rounded-2xl p-8 shadow-sm">
                <h2 className="text-3xl md:text-4xl font-serif font-bold text-[#1A1A1A] mb-6">
                    Where this data comes from
                </h2>
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-lg md:text-xl border-collapse">
                        <thead>
                            <tr className="border-b-2 border-[#E7DFCF] text-sm font-bold uppercase tracking-wider text-[#5B5750]">
                                <th className="pb-4 pr-4">What you see</th>
                                <th className="pb-4 pr-4">Source</th>
                                <th className="pb-4 pr-4">Cost</th>
                                <th className="pb-4">How fresh</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-[#E7DFCF]">
                            <tr>
                                <td className="py-4 pr-4 font-medium">Trend word, price, day change</td>
                                <td className="py-4 pr-4">Yahoo Finance (yfinance), NSE prices</td>
                                <td className="py-4 pr-4 text-[#00A651] font-bold">Free</td>
                                <td className="py-4 text-[#5B5750]">Every 15 min (~15 min delayed)</td>
                            </tr>
                            <tr>
                                <td className="py-4 pr-4 font-medium">RSI &amp; MACD</td>
                                <td className="py-4 pr-4">Worked out from price history (TradingView formulas)</td>
                                <td className="py-4 pr-4 text-[#00A651] font-bold">Free</td>
                                <td className="py-4 text-[#5B5750]">Every 15 min</td>
                            </tr>
                            <tr>
                                <td className="py-4 pr-4 font-medium">Company news</td>
                                <td className="py-4 pr-4">Google News (Moneycontrol, Economic Times, BQ Prime)</td>
                                <td className="py-4 pr-4 text-[#00A651] font-bold">Free</td>
                                <td className="py-4 text-[#5B5750]">Every hour</td>
                            </tr>
                            <tr>
                                <td className="py-4 pr-4 font-medium">NSE/BSE official filings</td>
                                <td className="py-4 pr-4"><em>Backlog</em> — added in the next step</td>
                                <td className="py-4 pr-4 text-[#00A651] font-bold">Free</td>
                                <td className="py-4 text-[#5B5750]">—</td>
                            </tr>
                            <tr>
                                <td className="py-4 pr-4 font-medium">Positions &amp; profit/loss</td>
                                <td className="py-4 pr-4"><em>Phase 1</em> — 2 Zerodha + 1 mStock</td>
                                <td className="py-4 pr-4 text-[#5B5750]">Zerodha ~₹500/mo each</td>
                                <td className="py-4 text-[#5B5750]">Every 15 min</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            {/* Footnote */}
            <p className="mt-10 text-center text-lg text-[#5B5750] border-t border-[#E7DFCF] pt-6 font-medium">
                Phase 0 — trend + news only.{" "}
                {snap.out_dir && (
                    <>
                        Data also written to <strong>{snap.out_dir}</strong> every refresh (board_latest + history for studying later).
                    </>
                )}
            </p>
        </div>
    );
}
