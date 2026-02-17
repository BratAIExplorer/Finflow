import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps {
    label: string;
    value: string;
    trend?: string;
    trendUp?: boolean;
    icon: LucideIcon;
    delay?: number;
}

export function StatCard({ label, value, trend, trendUp, icon: Icon, delay = 0 }: StatCardProps) {
    return (
        <div
            className={cn(
                "glass-surface p-6 rounded-2xl flex flex-col gap-4 relative overflow-hidden group hover:-translate-y-1 transition-transform duration-300",
                "animate-in fade-in slide-in-from-bottom-4 duration-700 fill-mode-backwards"
            )}
            style={{ animationDelay: `${delay}ms` }}
        >
            <div className="flex justify-between items-start">
                <div className="p-3 bg-white/5 rounded-xl group-hover:bg-white/10 transition-colors">
                    <Icon className="w-5 h-5 text-indigo-300" />
                </div>
                {trend && (
                    <div className={cn(
                        "px-2 py-1 rounded-full text-xs font-medium border",
                        trendUp
                            ? "bg-emerald-500/10 text-emerald-300 border-emerald-500/20"
                            : "bg-rose-500/10 text-rose-300 border-rose-500/20"
                    )}>
                        {trend}
                    </div>
                )}
            </div>

            <div>
                <h4 className="text-gray-400 text-sm font-medium">{label}</h4>
                <div className="text-2xl font-bold font-outfit mt-1 text-white">{value}</div>
            </div>

            {/* Hover Gradient Effect */}
            <div className="absolute inset-0 bg-gradient-to-tr from-indigo-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
        </div>
    );
}
