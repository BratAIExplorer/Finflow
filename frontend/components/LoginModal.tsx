"use client";

// Ported from C:\Antigravity\Fortress app/login/LoginForm.tsx — same validation,
// error-box and loading structure. Adapted to FinFlow: a glass modal (not a route),
// FastAPI JWT stored in localStorage instead of a NextAuth cookie, and no Google
// sign-in (FinFlow's backend has no OAuth).

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, ShieldCheck, Loader2 } from "lucide-react";
import { GlassInput } from "./ui/GlassInput";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const TOKEN_KEY = "finflow_token";

interface Props {
    isOpen: boolean;
    onClose: () => void;
    onAuthed: () => void;
}

export function LoginModal({ isOpen, onClose, onAuthed }: Props) {
    const [mode, setMode] = useState<"signin" | "register">("signin");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const reset = () => {
        setError("");
        setPassword("");
        setLoading(false);
    };

    async function signIn(mail: string, pass: string) {
        // FastAPI's OAuth2PasswordRequestForm wants form-encoded username/password.
        const body = new URLSearchParams({ username: mail, password: pass });
        const res = await fetch(`${API}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body,
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data?.detail || "Login failed. Please try again.");
        localStorage.setItem(TOKEN_KEY, data.access_token);
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        if (!email || !password) {
            setError("Please enter both email and password");
            return;
        }
        if (!email.includes("@")) {
            setError("Please enter a valid email address");
            return;
        }
        if (mode === "register" && password.length < 8) {
            setError("Password must be at least 8 characters");
            return;
        }

        setLoading(true);
        try {
            if (mode === "register") {
                const res = await fetch(`${API}/auth/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password }),
                });
                const data = await res.json().catch(() => ({}));
                if (!res.ok) throw new Error(data?.detail || "Could not create account");
            }
            await signIn(email, password);
            reset();
            onAuthed();
            onClose();
        } catch (err) {
            setError((err as Error).message);
            setLoading(false);
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
                    />
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md z-50"
                    >
                        <div className="glass-surface p-8 rounded-3xl border border-white/10 shadow-2xl relative" style={{ background: "rgba(8,12,24,0.98)" }}>
                            <button onClick={onClose} className="absolute top-4 right-4 p-2 rounded-full hover:bg-white/10 transition-colors text-gray-400 hover:text-white">
                                <X className="w-5 h-5" />
                            </button>

                            <div className="flex justify-center mb-4">
                                <div className="bg-indigo-500/10 p-3 rounded-2xl border border-indigo-500/20">
                                    <ShieldCheck className="h-7 w-7 text-indigo-400" />
                                </div>
                            </div>
                            <h2 className="text-2xl font-bold font-outfit text-center text-white">
                                {mode === "signin" ? "Sign in to FinFlow" : "Create your FinFlow account"}
                            </h2>
                            <p className="text-sm text-gray-400 text-center mt-1.5">Access your investment command center</p>

                            <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4">
                                {error && (
                                    <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm rounded-lg">
                                        {error}
                                    </div>
                                )}
                                <GlassInput
                                    label="Email Address"
                                    type="email"
                                    autoComplete="email"
                                    placeholder="you@example.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                                <GlassInput
                                    label="Password"
                                    type="password"
                                    autoComplete={mode === "signin" ? "current-password" : "new-password"}
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="mt-2 w-full py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 font-bold text-white shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40 active:scale-95 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                                >
                                    {loading ? <><Loader2 className="w-5 h-5 animate-spin" /> Authenticating…</> : mode === "signin" ? "Log in" : "Create account"}
                                </button>
                            </form>

                            <p className="mt-6 text-sm text-center text-gray-400">
                                {mode === "signin" ? (
                                    <>Don&apos;t have an account?{" "}
                                        <button onClick={() => { setMode("register"); setError(""); }} className="text-indigo-400 hover:underline">Create one</button>
                                        <br />
                                        <span className="text-xs text-gray-500">Forgot your password? Ask the admin to reset it — no self-serve reset yet.</span>
                                    </>
                                ) : (
                                    <>Already have an account?{" "}
                                        <button onClick={() => { setMode("signin"); setError(""); }} className="text-indigo-400 hover:underline">Sign in</button>
                                    </>
                                )}
                            </p>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
