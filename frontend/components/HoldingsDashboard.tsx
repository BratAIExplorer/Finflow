"use client";

import { useCallback, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, RefreshCw, Loader2 } from "lucide-react";
import { Holding } from "@/lib/holdingsFormat";
import { TOKEN_KEY } from "./LoginModal";
import { SummaryPanel } from "./portfolio/SummaryPanel";
import { HoldingsTable } from "./portfolio/HoldingsTable";

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
    if (!res.ok) {
        return 0.0;
    }
    const data = await res.json();
    return data.cash_balance || 0.0;
}

type Tab = "summary" | "holdings";

interface Props {
    isOpen: boolean;
    onClose: () => void;
}

export function HoldingsDashboard({ isOpen, onClose }: Props) {
    const [rows, setRows] = useState<Holding[]>([]);
    const [cash, setCash] = useState<number>(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [tab, setTab] = useState<Tab>("summary");

    const load = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const [holdingsData, cashData] = await Promise.all([
                fetchHoldings(),
                fetchCash()
            ]);
            setRows(holdingsData);
            setCash(cashData);
        } catch (e) {
            setError((e as Error).message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (isOpen) load();
    }, [isOpen, load]);

    const empty = !loading && !error && rows.length === 0;

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40"
                    />
                    <motion.div
                        initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 24 }}
                        className="fixed inset-0 z-50 mx-auto w-full max-w-none p-4 md:p-8"
                    >
                        <div className="glass-surface h-full w-full overflow-y-auto rounded-3xl border border-white/10 shadow-2xl p-6 md:p-10" style={{ background: "rgba(8,12,24,0.98)" }}>
                            <button
                                onClick={onClose}
                                className="absolute top-5 right-6 p-2 rounded-full hover:bg-white/10 transition-colors text-gray-400 hover:text-white"
                            >
                                <X className="w-5 h-5" />
                            </button>

                            <div className="flex flex-wrap items-end justify-between gap-4 mb-6">
                                <div>
                                    <h2 className="text-3xl font-bold font-outfit prime-gradient-text">Portfolio</h2>
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

                            {/* Tabs */}
                            <div className="flex gap-1 mb-8 p-1 rounded-xl bg-white/5 w-fit">
                                {(["summary", "holdings"] as Tab[]).map((t) => (
                                    <button
                                        key={t}
                                        onClick={() => setTab(t)}
                                        className={`px-4 py-2 rounded-lg text-sm font-semibold capitalize transition-colors ${
                                            tab === t ? "bg-white/10 text-white" : "text-gray-400 hover:text-white"
                                        }`}
                                    >
                                        {t}
                                    </button>
                                ))}
                            </div>

                            {error && (
                                <p className="text-sm text-rose-400 mb-6">
                                    {error.includes("401") || error.toLowerCase().includes("credential")
                                        ? "Session expired — sign in again."
                                        : error}
                                </p>
                            )}

                            {empty && (
                                <p className="text-sm text-gray-400">
                                    No holdings yet. Open <strong className="text-gray-200">Plugins</strong>, add a broker account,
                                    then hit <strong className="text-gray-200">Sync now</strong>.
                                </p>
                            )}

                            {rows.length > 0 && tab === "summary" && <SummaryPanel rows={rows} cash={cash} />}
                            {rows.length > 0 && tab === "holdings" && <HoldingsTable rows={rows} onReload={load} />}
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
