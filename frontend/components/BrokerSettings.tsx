"use client";

import { useCallback, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, RefreshCw, Trash2, Pencil, Plus, HelpCircle, Loader2, ArrowLeft } from "lucide-react";
import { GlassInput } from "./ui/GlassInput";
import { GlassSelect } from "./ui/GlassSelect";

// --- stolen from TradingBot's build_broker_tab: broker dropdown -> per-broker fields + "where do I get this?" help.
// Dropped: the flat 6-field form, manual access-token box, paper-trading toggles.
type Field = { key: string; label: string; help: string; secret?: boolean };

const BROKER_FIELDS: Record<string, Field[]> = {
    mstock: [
        { key: "api_key", label: "API Key", help: "mstock.com -> Trading API section" },
        { key: "username", label: "Client ID", help: "Your mStock login ID" },
        { key: "password", label: "Password", help: "Your mStock login password", secret: true },
        { key: "totp_secret", label: "TOTP Secret", help: "The static Base32 secret string (e.g. JBSWY3DPEHPK3PXP) shown when you enable TOTP. DO NOT enter the 6-digit pin.", secret: true },
    ],
    zerodha: [
        { key: "api_key", label: "API Key", help: "kite.trade -> your Connect app" },
        { key: "api_secret", label: "API Secret", help: "Same Connect app page as the API Key", secret: true },
        { key: "redirect_url", label: "Redirect URL", help: "Must match the redirect URL set on your Kite Connect app" },
    ],
};

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const getToken = () => (typeof window !== "undefined" ? localStorage.getItem("finflow_token") : null);

async function api(path: string, opts: RequestInit = {}) {
    const res = await fetch(`${API}/holdings${path}`, {
        ...opts,
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${getToken()}`, ...(opts.headers || {}) },
    });
    if (!res.ok) throw new Error((await res.json().catch(() => ({})))?.detail || `Request failed (${res.status})`);
    return res.json();
}

type Account = {
    id: string;
    plugin_name: string;
    label: string;
    last_synced: string | null;
    last_sync_error: string | null;
};

interface Props {
    isOpen: boolean;
    onClose: () => void;
}

export function BrokerSettings({ isOpen, onClose }: Props) {
    const [accounts, setAccounts] = useState<Account[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [view, setView] = useState<"list" | "form">("list");
    const [editing, setEditing] = useState<Account | null>(null);

    const load = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            setAccounts(await api("/accounts"));
        } catch (e) {
            setError((e as Error).message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (isOpen) {
            setView("list");
            setEditing(null);
            load();
        }
    }, [isOpen, load]);

    const busy = async (fn: () => Promise<unknown>) => {
        setLoading(true);
        setError(null);
        try {
            await fn();
            await load();
        } catch (e) {
            setError((e as Error).message);
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
                        className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-lg z-50"
                    >
                        <div className="glass-surface p-8 rounded-3xl border border-white/10 shadow-2xl relative max-h-[85vh] overflow-y-auto" style={{ background: "rgba(8,12,24,0.98)" }}>
                            <button onClick={onClose} className="absolute top-4 right-4 p-2 rounded-full hover:bg-white/10 transition-colors text-gray-400 hover:text-white">
                                <X className="w-5 h-5" />
                            </button>

                            {view === "list" ? (
                                <>
                                    <h2 className="text-2xl font-bold font-outfit mb-6 text-white">Broker Accounts</h2>

                                    {error && <p className="text-sm text-rose-400 mb-4">{error}</p>}
                                    {loading && <Loader2 className="w-5 h-5 animate-spin text-gray-400 mb-4" />}

                                    <div className="flex flex-col gap-3">
                                        {accounts.map((a) => (
                                            <div key={a.id} className="glass-surface rounded-xl p-4 flex flex-col gap-2">
                                                <div className="flex items-center justify-between">
                                                    <div>
                                                        <p className="font-semibold text-white">{a.label}</p>
                                                        <p className="text-xs text-gray-500 uppercase tracking-wider">{a.plugin_name}</p>
                                                    </div>
                                                    <div className="flex gap-1">
                                                        <IconBtn title="Sync now" onClick={() => busy(() => api(`/accounts/${a.id}/sync`, { method: "POST" }))}>
                                                            <RefreshCw className="w-4 h-4" />
                                                        </IconBtn>
                                                        <IconBtn title="Edit" onClick={() => { setEditing(a); setView("form"); }}>
                                                            <Pencil className="w-4 h-4" />
                                                        </IconBtn>
                                                        <IconBtn title="Delete" onClick={() => {
                                                            if (confirm(`Remove "${a.label}"? Its synced holdings are deleted too.`))
                                                                busy(() => api(`/accounts/${a.id}`, { method: "DELETE" }));
                                                        }}>
                                                            <Trash2 className="w-4 h-4" />
                                                        </IconBtn>
                                                    </div>
                                                </div>
                                                <p className="text-xs text-gray-500">
                                                    {a.last_sync_error
                                                        ? <span className="text-rose-400">Last sync failed: {a.last_sync_error}</span>
                                                        : a.last_synced
                                                            ? `Last synced ${new Date(a.last_synced).toLocaleString()}`
                                                            : "Never synced"}
                                                </p>
                                            </div>
                                        ))}
                                        {!loading && accounts.length === 0 && (
                                            <p className="text-sm text-gray-500">No accounts yet. Add your first broker below.</p>
                                        )}
                                    </div>

                                    <button
                                        onClick={() => { setEditing(null); setView("form"); }}
                                        className="mt-6 w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 font-bold text-white shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40 active:scale-95 transition-all flex items-center justify-center gap-2"
                                    >
                                        <Plus className="w-5 h-5" /> Add Broker Account
                                    </button>
                                </>
                            ) : (
                                <AccountForm
                                    editing={editing}
                                    onBack={() => setView("list")}
                                    onSaved={async () => { setView("list"); await load(); }}
                                />
                            )}
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}

function IconBtn({ title, onClick, children }: { title: string; onClick: () => void; children: React.ReactNode }) {
    return (
        <button title={title} onClick={onClick} className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors">
            {children}
        </button>
    );
}

function AccountForm({ editing, onBack, onSaved }: { editing: Account | null; onBack: () => void; onSaved: () => void }) {
    const [broker, setBroker] = useState(editing?.plugin_name || "mstock");
    const [label, setLabel] = useState(editing?.label || "");
    const [creds, setCreds] = useState<Record<string, string>>({});
    const [showSecrets, setShowSecrets] = useState(false);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fields = BROKER_FIELDS[broker];

    const submit = async () => {
        setSaving(true);
        setError(null);
        try {
            if (editing) {
                // credentials only sent if the user actually typed new ones
                const filled = Object.fromEntries(Object.entries(creds).filter(([, v]) => v.trim() !== ""));
                const body: Record<string, unknown> = { label };
                if (Object.keys(filled).length === fields.length) body.credentials = filled;
                else if (Object.keys(filled).length > 0) throw new Error("To change credentials, fill in every field for this broker.");
                await api(`/accounts/${editing.id}`, { method: "PATCH", body: JSON.stringify(body) });
            } else {
                await api("/accounts", {
                    method: "POST",
                    body: JSON.stringify({ plugin_name: broker, label, credentials: creds }),
                });
            }
            onSaved();
        } catch (e) {
            setError((e as Error).message);
        } finally {
            setSaving(false);
        }
    };

    return (
        <form className="flex flex-col gap-5" onSubmit={(e) => { e.preventDefault(); submit(); }}>
            <button type="button" onClick={onBack} className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors self-start">
                <ArrowLeft className="w-4 h-4" /> Back
            </button>
            <h2 className="text-2xl font-bold font-outfit text-white">{editing ? "Edit Account" : "Add Broker Account"}</h2>

            {!editing && (
                <GlassSelect
                    label="Broker"
                    value={broker}
                    onChange={(e) => { setBroker(e.target.value); setCreds({}); }}
                    options={[
                        { value: "mstock", label: "mStock (Mirae Asset)" },
                        { value: "zerodha", label: "Zerodha (Kite)" },
                    ]}
                />
            )}

            <GlassInput
                label="Account Name"
                placeholder={`e.g. "Dad's mStock"`}
                value={label}
                onChange={(e) => setLabel(e.target.value)}
            />

            {editing && (
                <p className="text-xs text-gray-500 -mt-2">
                    Leave the credential fields blank to keep the current ones. Fill in all {fields.length} to replace them.
                </p>
            )}

            {fields.map((f) => (
                <div key={f.key} className="flex flex-col gap-1">
                    <GlassInput
                        label={f.label}
                        type={f.secret && !showSecrets ? "password" : "text"}
                        placeholder={editing ? "unchanged" : ""}
                        value={creds[f.key] || ""}
                        onChange={(e) => setCreds({ ...creds, [f.key]: e.target.value })}
                        autoComplete="off"
                    />
                    <span className="text-xs text-gray-500 ml-1 flex items-center gap-1">
                        <HelpCircle className="w-3 h-3 shrink-0" /> {f.help}
                    </span>
                </div>
            ))}

            <label className="flex items-center gap-2 text-sm text-gray-400 cursor-pointer">
                <input type="checkbox" checked={showSecrets} onChange={(e) => setShowSecrets(e.target.checked)} />
                Show secrets
            </label>

            {broker === "zerodha" && !editing && (
                <p className="text-xs text-gray-500">
                    After saving, open the account and hit <strong>Sync now</strong> — Zerodha will ask you to log in once per day.
                </p>
            )}

            {error && <p className="text-sm text-rose-400">{error}</p>}

            <button
                type="submit"
                disabled={saving || !label}
                className="mt-2 w-full py-4 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 font-bold text-white shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40 active:scale-95 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
                {saving ? <><Loader2 className="w-5 h-5 animate-spin" /> Saving...</> : editing ? "Save Changes" : "Add Account"}
            </button>
        </form>
    );
}
