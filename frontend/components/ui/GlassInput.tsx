import { InputHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

interface GlassInputProps extends InputHTMLAttributes<HTMLInputElement> {
    label: string;
    error?: string;
}

export const GlassInput = forwardRef<HTMLInputElement, GlassInputProps>(
    ({ className, label, error, ...props }, ref) => {
        return (
            <div className="flex flex-col gap-2 w-full">
                <label className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider ml-1">
                    {label}
                </label>
                <input
                    ref={ref}
                    className={cn(
                        "glass-surface px-4 py-3.5 rounded-xl text-base text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all",
                        error && "border-rose-500/50 focus:ring-rose-500/20",
                        className
                    )}
                    {...props}
                />
                {error && <span className="text-sm text-rose-500 dark:text-rose-400 ml-1">{error}</span>}
            </div>
        );
    }
);
GlassInput.displayName = "GlassInput";
