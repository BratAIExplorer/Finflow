import { SelectHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

interface GlassSelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
    label: string;
    error?: string;
    options: { value: string; label: string }[];
}

export const GlassSelect = forwardRef<HTMLSelectElement, GlassSelectProps>(
    ({ className, label, error, options, ...props }, ref) => {
        return (
            <div className="flex flex-col gap-2 w-full">
                <label className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider ml-1">
                    {label}
                </label>
                <div className="relative">
                    <select
                        ref={ref}
                        className={cn(
                            "glass-surface w-full px-4 py-3.5 rounded-xl text-base text-slate-900 dark:text-white appearance-none focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all cursor-pointer",
                            error && "border-rose-500/50 focus:ring-rose-500/20",
                            className
                        )}
                        {...props}
                    >
                        {options.map((opt) => (
                            <option key={opt.value} value={opt.value} className="bg-white text-slate-900 dark:bg-[#0f172a] dark:text-white text-base">
                                {opt.label}
                            </option>
                        ))}
                    </select>
                    <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 dark:text-gray-400 text-xs">
                        ▼
                    </div>
                </div>
                {error && <span className="text-sm text-rose-500 dark:text-rose-400 ml-1">{error}</span>}
            </div>
        );
    }
);
GlassSelect.displayName = "GlassSelect";
