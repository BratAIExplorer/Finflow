"use client";

import { useEffect, useState } from "react";
import { Newspaper, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { TOKEN_KEY } from "@/components/LoginModal";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface NewsItem {
    id: string;
    symbol: string;
    name: string;
    headline: string;
    source: string;
    time: string;
    sentiment: "pos" | "neg" | "neu";
    important: boolean;
}

const SENTIMENT_ICON = { pos: TrendingUp, neg: TrendingDown, neu: Minus };
const SENTIMENT_COLOR = { pos: "text-emerald-400", neg: "text-rose-400", neu: "text-gray-500" };

export function NewsPanel() {
    const [items, setItems] = useState<NewsItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const token = typeof window !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null;
        fetch(`${API}/news/`, { headers: { Authorization: `Bearer ${token}` } })
            .then(async (res) => {
                if (!res.ok) throw new Error((await res.json().catch(() => ({})))?.detail || `Request failed (${res.status})`);
                return res.json();
            })
            .then(setItems)
            .catch((e) => setError((e as Error).message))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <p className="text-lg text-gray-400">Loading news…</p>;
    if (error) return <p className="text-lg text-rose-400">{error}</p>;
    if (items.length === 0) return <p className="text-lg text-gray-400">No recent news for your holdings.</p>;

    return (
        <div className="flex flex-col gap-3">
            {items.map((item) => {
                const Icon = SENTIMENT_ICON[item.sentiment];
                return (
                    <div key={item.id} className="glass-surface rounded-xl p-4 flex items-start gap-4">
                        <Icon className={`w-5 h-5 mt-1 shrink-0 ${SENTIMENT_COLOR[item.sentiment]}`} />
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                                <span className="text-sm font-bold text-indigo-300">{item.symbol}</span>
                                {item.important && (
                                    <span className="text-[10px] uppercase tracking-wider font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300">
                                        Material
                                    </span>
                                )}
                            </div>
                            <p className="text-lg text-gray-100 leading-snug">{item.headline}</p>
                            <p className="text-sm text-gray-500 mt-1">{item.source} · {item.time}</p>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
