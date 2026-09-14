"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { RefreshCw, Loader2, ArrowLeft } from "lucide-react";
import { Holding } from "@/lib/holdingsFormat";
import { LoginModal, TOKEN_KEY } from "@/components/LoginModal";
import { SummaryPanel } from "@/components/portfolio/SummaryPanel";
import { HoldingsTable } from "@/components/portfolio/HoldingsTable";
import { NewsPanel } from "@/components/portfolio/NewsPanel";
import { MarketBoardPanel } from "@/components/portfolio/MarketBoardPanel";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const getToken = () => (typeof window !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null);

async function fetchHoldings(): Promise<Holding[]> {
    const res = await fetch(`${API}/holdings/`, { headers: { Authorization: `Bearer ${getToken()}` } });
    if (!res.ok) {
        const detail = (await res.json().catch(() => ({})))?.detail;
        throw new Error(detail || `Request failed (${res.status})`);
    }
    return res.json();
}

async function fetchCash(): Promise<number> {
    const res = await fetch(`${API}/holdings/cash`, { headers: { Authorization: `Bearer ${getToken()}` } });
    if (!res.ok) return 0.0;
    const data = await res.json();
    return data.cash_balance || 0.0;
}

type Tab = "summary" | "holdings" | "news" | "board";
const TABS: { id: Tab; label: string }[] = [
    { id: "summary", label: "Summary" },
    { id: "holdings", label: "Holdings" },
    { id: "news", label: "News" },
    { id: "board", label: "Market Board" },
];

export default function PortfolioPage() {
    const router = useRouter();
    const [rows, setRows] = useState<Holding[]>([]);
    const [cash, setCash] = useState<number>(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [tab, setTab] = useState<Tab>("summary");
    const [showLogin, setShowLogin] = useState(false);

    const load = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const [holdingsData, cashData] = await Promise.all([fetchHoldings(), fetchCash()]);
            setRows(holdingsData);
            setCash(cashData);
        } catch (e) {
            setError((e as Error).message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (!getToken()) {
            router.replace("/");
            return;
        }
        load();
    }, [load, router]);

    const empty = !loading && !error && rows.length === 0;
    const sessionExpired = !!error && (error.includes("401") || error.toLowerCase().includes("credential"));

    return (
        <div className="min-h-screen bg-[#030712] text-white p-6 md:p-10">
            <div className="max-w-6xl mx-auto">
                <Link href="/" className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors mb-6">
                    <ArrowLeft className="w-4 h-4" /> Back
                </Link>

                <div className="flex flex-wrap items-end justify-between gap-4 mb-6">
                    <div>
                        <h1 className="text-3xl font-bold font-outfit prime-gradient-text">Portfolio</h1>
                        <p className="text-sm text-gray-400 mt-1.5">
                            Combined view across your linked broker accounts · numbers only, no buy/sell calls
                        </p>
                    </div>
                    <button
                        onClick={load}
                        disabled={loading}
                        className="flex items-center gap-2 text-sm text-gray-300 hover:text-white transition-colors disabled:opacity-50"
                    >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                        Refresh
                    </button>
                </div>

                <div className="flex gap-1 mb-8 p-1 rounded-xl bg-white/5 w-fit">
                    {TABS.map((t) => (
                        <button
                            key={t.id}
                            onClick={() => setTab(t.id)}
                            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
                                tab === t.id ? "bg-white/10 text-white" : "text-gray-400 hover:text-white"
                            }`}
                        >
                            {t.label}
                        </button>
                    ))}
                </div>

                {error && (
                    <div className="flex items-center gap-3 mb-6">
                        <p className="text-sm text-rose-400">
                            {sessionExpired ? "Session expired — sign in again." : error}
                        </p>
                        {sessionExpired && (
                            <button
                                onClick={() => setShowLogin(true)}
                                className="text-sm font-semibold text-indigo-400 hover:text-indigo-300 underline underline-offset-2"
                            >
                                Sign in
                            </button>
                        )}
                    </div>
                )}

                {empty && tab !== "news" && tab !== "board" && (
                    <p className="text-sm text-gray-400">
                        No holdings yet. Open <strong className="text-gray-200">Plugins</strong>, add a broker account,
                        then hit <strong className="text-gray-200">Sync now</strong>.
                    </p>
                )}

                {rows.length > 0 && tab === "summary" && <SummaryPanel rows={rows} cash={cash} />}
                {rows.length > 0 && tab === "holdings" && <HoldingsTable rows={rows} onReload={load} />}
                {tab === "news" && (rows.length > 0 ? <NewsPanel /> : (
                    <p className="text-sm text-gray-400">Add holdings first — news is matched to your portfolio.</p>
                ))}
                {tab === "board" && <MarketBoardPanel />}
            </div>
            <LoginModal
                isOpen={showLogin}
                onClose={() => setShowLogin(false)}
                onAuthed={() => {
                    setShowLogin(false);
                    load();
                }}
            />
        </div>
    );
}
