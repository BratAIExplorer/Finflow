"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { GlassInput } from "./ui/GlassInput";
import { GlassSelect } from "./ui/GlassSelect";
import { motion, AnimatePresence } from "framer-motion";
import { X, Check, Loader2 } from "lucide-react";

const assetSchema = z.object({
    category: z.string().min(1, "Category is required"),
    name: z.string().min(2, "Name must be at least 2 characters"),
    institution: z.string().optional(),
    value: z.number().min(0, "Value cannot be negative"),
    currency: z.string().min(1, "Currency is required"),
});

type AssetFormData = z.infer<typeof assetSchema>;

interface AddAssetFormProps {
    isOpen: boolean;
    onClose: () => void;
}

export function AddAssetForm({ isOpen, onClose }: AddAssetFormProps) {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [success, setSuccess] = useState(false);

    const {
        register,
        handleSubmit,
        reset,
        formState: { errors },
    } = useForm<AssetFormData>({
        resolver: zodResolver(assetSchema),
        defaultValues: {
            currency: "MYR",
            category: "bank",
        },
    });

    const onSubmit = async (data: AssetFormData) => {
        setIsSubmitting(true);
        // Simulate API call for now
        await new Promise((resolve) => setTimeout(resolve, 1500));
        console.log("Submitting Asset:", data);

        // TODO: Connect to actual API
        // await fetch('/api/assets', { method: 'POST', body: JSON.stringify(data) });

        setSuccess(true);
        setTimeout(() => {
            setSuccess(false);
            reset();
            onClose();
            setIsSubmitting(false);
        }, 1000);
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
                    />

                    {/* Modal */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md z-50"
                    >
                        <div className="glass-surface p-8 rounded-3xl border border-white/10 shadow-2xl relative">
                            <button
                                onClick={onClose}
                                className="absolute top-4 right-4 p-2 rounded-full hover:bg-white/10 transition-colors text-gray-400 hover:text-white"
                            >
                                <X className="w-5 h-5" />
                            </button>

                            <h2 className="text-2xl font-bold font-outfit mb-6 text-white">Add Manual Asset</h2>

                            {success ? (
                                <div className="flex flex-col items-center justify-center py-12 gap-4">
                                    <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                                        <Check className="w-8 h-8" />
                                    </div>
                                    <p className="text-emerald-300 font-medium">Asset Added Successfully!</p>
                                </div>
                            ) : (
                                <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5">
                                    <GlassSelect
                                        label="Category"
                                        options={[
                                            { value: "bank", label: "Bank Account" },
                                            { value: "property", label: "Property / Real Estate" },
                                            { value: "vehicle", label: "Vehicle" },
                                            { value: "insurance", label: "Insurance Policy" },
                                            { value: "other", label: "Other Asset" },
                                        ]}
                                        {...register("category")}
                                        error={errors.category?.message}
                                    />

                                    <GlassInput
                                        label="Asset Name"
                                        placeholder="e.g. Maybank Savings, Condo Unit"
                                        {...register("name")}
                                        error={errors.name?.message}
                                    />

                                    <div className="grid grid-cols-2 gap-4">
                                        <GlassInput
                                            label="Value"
                                            type="number"
                                            placeholder="0.00"
                                            {...register("value", { valueAsNumber: true })}
                                            error={errors.value?.message}
                                        />
                                        <GlassSelect
                                            label="Currency"
                                            options={[
                                                { value: "MYR", label: "MYR - Ringgit" },
                                                { value: "USD", label: "USD - Dollar" },
                                                { value: "INR", label: "INR - Rupee" },
                                                { value: "SGD", label: "SGD - Dollar" },
                                            ]}
                                            {...register("currency")}
                                            error={errors.currency?.message}
                                        />
                                    </div>

                                    <GlassInput
                                        label="Institution (Optional)"
                                        placeholder="e.g. Maybank, Prudential"
                                        {...register("institution")}
                                        error={errors.institution?.message}
                                    />

                                    <button
                                        type="submit"
                                        disabled={isSubmitting}
                                        className="mt-4 w-full py-4 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 font-bold text-white shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40 active:scale-95 transition-all flex items-center justify-center gap-2 "
                                    >
                                        {isSubmitting ? (
                                            <>
                                                <Loader2 className="w-5 h-5 animate-spin" />
                                                Saving...
                                            </>
                                        ) : (
                                            "Save Asset"
                                        )}
                                    </button>
                                </form>
                            )}
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
