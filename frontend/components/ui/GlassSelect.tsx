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
                <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider ml-1">
                    {label}
                </label>
                <div className="relative">
                    <select
                        ref={ref}
                        className={cn(
                            "glass-surface w-full px-4 py-3 rounded-xl text-white appearance-none focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all cursor-pointer bg-none",
                            error && "border-rose-500/50 focus:ring-rose-500/20",
                            className
                        )}
                        {...props}
                    >
                        {options.map((opt) => (
                            <option key={opt.value} value={opt.value} className="bg-[#0f172a] text-white">
                                {opt.label}
                            </option>
                        ))}
                    </select>
                    <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                        ▼
                    </div>
                </div>
                {error && <span className="text-xs text-rose-400 ml-1">{error}</span>}
            </div>
        );
    }
);
GlassSelect.displayName = "GlassSelect";
