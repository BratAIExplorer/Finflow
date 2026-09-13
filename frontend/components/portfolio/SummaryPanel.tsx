"use client";

import { useEffect, useMemo, useState } from "react";
import {
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Tooltip,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    LabelList,
    Legend,
} from "recharts";
import {
    Holding,
    inr,
    pctLabel,
    plColor,
    summarise,
    bySector,
    byCapTier,
    topByInvestment,
    topByReturns,
    CAP_TIERS,
} from "@/lib/holdingsFormat";

const PIE_COLORS = ["#6366f1", "#22d3ee", "#34d399", "#f59e0b", "#a78bfa", "#f472b6", "#60a5fa", "#4ade80"];
const CARD = "glass-surface rounded-2xl p-5";

export function SummaryPanel({ rows }: { rows: Holding[] }) {
    const [tier, setTier] = useState<string>("All");

    // The dashboard opens inside an animating modal; give layout a beat to
    // settle before recharts measures its ResponsiveContainers, otherwise
    // the first paint sizes every chart to ~0 width.
    const [ready, setReady] = useState(false);
    useEffect(() => {
        const t = setTimeout(() => setReady(true), 380);
        return () => clearTimeout(t);
    }, []);

    const filtered = useMemo(
        () => (tier === "All" ? rows : rows.filter((r) => (r.cap_tier ?? "Unclassified") === tier)),
        [rows, tier],
    );

    const s = summarise(filtered);
    const sectors = bySector(filtered);
    const caps = byCapTier(filtered);
    const topInvest = topByInvestment(filtered);
    const topReturns = topByReturns(filtered);
    const investVsReturns = topInvest.map((d) => ({ name: d.name, Invested: Math.round(d.invested), Returns: Math.round(d.returns) }));

    if (filtered.length === 0) {
        return <p className="text-sm text-gray-400">No holdings in the {tier} bucket.</p>;
    }

    const chartFallback = <div className="h-[230px] flex items-center justify-center text-xs text-gray-600">Loading chart…</div>;

    return (
        <div className="flex flex-col gap-5">
            {/* KPI tiles */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <Kpi label="Current Value" value={inr(s.currentValue)} />
                <Kpi label="Invested Amount" value={inr(s.invested)} />
                <Kpi label="Total Returns" value={inr(s.pnl)} color={plColor(s.pnl)} />
                <Kpi label="Growth" value={pctLabel(s.pnlPct)} color={plColor(s.pnl)} />
            </div>

            {/* Cap-tier filter */}
            <div className="flex flex-wrap gap-2">
                {["All", ...CAP_TIERS].map((t) => (
                    <button
                        key={t}
                        onClick={() => setTier(t)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                            tier === t ? "bg-indigo-600 text-white" : "bg-white/5 text-gray-400 hover:text-white"
                        }`}
                    >
                        {t}
                    </button>
                ))}
            </div>

            {/* Row: sector pie · cap donut · top 5 invested */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div className={CARD}>
                    <h3 className="text-sm font-bold text-gray-300 mb-2">Investment by Sector</h3>
                    {ready ? <SlicePie data={sectors} innerRadius={0} /> : chartFallback}
                </div>
                <div className={CARD}>
                    <h3 className="text-sm font-bold text-gray-300 mb-2">Investment by Capitalization</h3>
                    {ready ? <SlicePie data={caps} innerRadius={55} /> : chartFallback}
                </div>
                <div className={CARD}>
                    <h3 className="text-sm font-bold text-gray-300 mb-2">Top 5 Companies by Investment</h3>
                    {ready ? <RankBar data={topInvest.map((d) => ({ name: d.name, value: Math.round(d.invested) }))} color="#6366f1" /> : chartFallback}
                </div>
            </div>

            {/* Row: invested vs returns · top 5 returns */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div className={CARD}>
                    <h3 className="text-sm font-bold text-gray-300 mb-2">Invested vs Returns</h3>
                    {!ready ? chartFallback : (
                    <ResponsiveContainer width="100%" height={240} minWidth={1} minHeight={1}>
                        <BarChart data={investVsReturns} layout="vertical" margin={{ left: 20, right: 24 }}>
                            <XAxis type="number" hide />
                            <YAxis type="category" dataKey="name" width={72} tick={{ fill: "#9ca3af", fontSize: 11 }} axisLine={false} tickLine={false} />
                            <Tooltip {...tooltipProps} />
                            <Bar isAnimationActive={false} dataKey="Invested" fill="#6366f1" radius={[0, 4, 4, 0]} barSize={10} />
                            <Bar isAnimationActive={false} dataKey="Returns" fill="#34d399" radius={[0, 4, 4, 0]} barSize={10} />
                        </BarChart>
                    </ResponsiveContainer>
                    )}
                </div>
                <div className={CARD}>
                    <h3 className="text-sm font-bold text-gray-300 mb-2">Top 5 Companies by Returns</h3>
                    {!ready ? chartFallback : (
                    <ResponsiveContainer width="100%" height={240} minWidth={1} minHeight={1}>
                        <BarChart data={topReturns.map((d) => ({ name: d.name, value: Math.round(d.returns) }))} margin={{ top: 16, left: 4, right: 4 }}>
                            <XAxis dataKey="name" tick={{ fill: "#9ca3af", fontSize: 10 }} axisLine={false} tickLine={false} interval={0} />
                            <YAxis hide />
                            <Tooltip {...tooltipProps} />
                            <Bar isAnimationActive={false} dataKey="value" radius={[4, 4, 0, 0]} barSize={34}>
                                {topReturns.map((d, i) => (
                                    <Cell key={i} fill={d.returns >= 0 ? "#34d399" : "#fb7185"} />
                                ))}
                                <LabelList dataKey="value" position="top" formatter={money} style={{ fill: "#9ca3af", fontSize: 10 }} />
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                    )}
                </div>
            </div>
        </div>
    );
}

const money = (v: unknown) => inr(Number(v) || 0);

const tooltipProps = {
    contentStyle: { background: "#0d1220", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 10, fontSize: 12 },
    labelStyle: { color: "#e5e7eb" },
    formatter: money,
};

function Kpi({ label, value, color }: { label: string; value: string; color?: string }) {
    return (
        <div className="glass-surface rounded-xl p-5 flex flex-col gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">{label}</span>
            <span className="text-2xl font-bold font-outfit tabular-nums" style={color ? { color } : undefined}>{value}</span>
        </div>
    );
}

function SlicePie({ data, innerRadius }: { data: { name: string; value: number; pct: number }[]; innerRadius: number }) {
    return (
        <ResponsiveContainer width="100%" height={230} minWidth={1} minHeight={1}>
            <PieChart>
                <Pie isAnimationActive={false} data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={innerRadius} outerRadius={90} paddingAngle={2}>
                    {data.map((_, i) => (
                        <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} stroke="#0a0f1e" strokeWidth={2} />
                    ))}
                </Pie>
                <Tooltip {...tooltipProps} />
                <Legend
                    verticalAlign="bottom"
                    height={44}
                    formatter={(name: unknown, entry: unknown) => {
                        const pct = (entry as { payload?: { pct?: number } })?.payload?.pct;
                        return pct != null ? `${name} (${pct.toFixed(0)}%)` : String(name);
                    }}
                    wrapperStyle={{ fontSize: 10, color: "#9ca3af" }}
                />
            </PieChart>
        </ResponsiveContainer>
    );
}

function RankBar({ data, color }: { data: { name: string; value: number }[]; color: string }) {
    return (
        <ResponsiveContainer width="100%" height={230} minWidth={1} minHeight={1}>
            <BarChart data={data} layout="vertical" margin={{ left: 24, right: 40 }}>
                <XAxis type="number" hide />
                <YAxis type="category" dataKey="name" width={72} tick={{ fill: "#9ca3af", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip {...tooltipProps} />
                <Bar isAnimationActive={false} dataKey="value" fill={color} radius={[0, 4, 4, 0]} barSize={18}>
                    <LabelList dataKey="value" position="right" formatter={money} style={{ fill: "#9ca3af", fontSize: 10 }} />
                </Bar>
            </BarChart>
        </ResponsiveContainer>
    );
}
