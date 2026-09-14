"use client";

import { motion, Variants } from "framer-motion";
import { ArrowRight, BarChart3, Wallet, ShieldCheck, Globe, Zap, Plus } from "lucide-react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { StatCard } from "@/components/ui/StatCard";
import { PortfolioChart } from "@/components/ui/PortfolioChart";
import { AddAssetForm } from "@/components/AddAssetForm";
import { BrokerSettings } from "@/components/BrokerSettings";
import { LoginModal, TOKEN_KEY } from "@/components/LoginModal";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useEffect, useState } from "react";

export default function Home() {
  const router = useRouter();
  const [isAddAssetOpen, setIsAddAssetOpen] = useState(false);
  const [isBrokerOpen, setIsBrokerOpen] = useState(false);
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    setAuthed(!!localStorage.getItem(TOKEN_KEY));
  }, []);

  const signOut = () => {
    localStorage.removeItem(TOKEN_KEY);
    setAuthed(false);
  };

  // A view that needs auth calls this; opens the login modal if not signed in.
  const requireAuth = (open: () => void) => () => (authed ? open() : setIsLoginOpen(true));
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.3,
      },
    },
  };

  const itemVariants: any = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } },
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#030712] text-slate-900 dark:text-white flex flex-col items-center justify-center p-6 md:p-12 relative overflow-hidden font-inter selection:bg-indigo-500/30 transition-colors duration-300">
      {/* Dynamic Background Orbs */}
      <div className="bg-prime-orb top-[-10%] left-[-5%] w-[650px] h-[650px] bg-indigo-500/25 dark:bg-indigo-600/30 blur-[130px]" />
      <div className="bg-prime-orb bottom-[-15%] right-[-5%] w-[550px] h-[550px] bg-blue-500/20 dark:bg-blue-600/20 blur-[120px]" />
      <div className="bg-prime-orb top-[20%] right-[10%] w-[350px] h-[350px] bg-purple-500/15 dark:bg-purple-600/10 blur-[90px]" />

      {/* Navigation - Glass Overlay with Theme Toggle */}
      <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-full max-w-2xl px-4">
        <div className="glass-surface py-3 px-6 md:px-8 rounded-full flex items-center justify-between glass-border shadow-2xl">
          <div className="text-2xl font-extrabold font-outfit tracking-tighter prime-gradient-text">FINFLOW</div>
          <div className="flex items-center gap-6 text-base font-semibold text-slate-600 dark:text-gray-400">
            <button onClick={requireAuth(() => router.push("/portfolio"))} className="hover:text-indigo-600 dark:hover:text-white transition-colors">Portfolio</button>
            <button onClick={requireAuth(() => setIsBrokerOpen(true))} className="hover:text-indigo-600 dark:hover:text-white transition-colors">Plugins</button>
            <a href="#" className="hover:text-indigo-600 dark:hover:text-white transition-colors">Family</a>
            {authed ? (
              <button onClick={signOut} className="hover:text-indigo-600 dark:hover:text-white transition-colors">Sign out</button>
            ) : (
              <button onClick={() => setIsLoginOpen(true)} className="text-indigo-500 dark:text-indigo-300 hover:text-indigo-600 dark:hover:text-white transition-colors">Sign in</button>
            )}
          </div>
          {/* Light / Dark Mode Switcher */}
          <div className="flex items-center gap-2">
            <ThemeToggle />
          </div>
        </div>
      </nav>

      <main className="z-10 max-w-6xl w-full flex flex-col items-center pt-24 pb-12">
        <motion.div
          className="text-center mb-16"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.div variants={itemVariants} className="inline-flex items-center gap-2.5 px-5 py-2 rounded-full glass-surface mb-8 glass-border">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-blue-500"></span>
            </span>
            <span className="text-xs md:text-sm uppercase tracking-wider font-bold text-indigo-700 dark:text-blue-200">
              Connectors Online • Multi-Currency
            </span>
          </motion.div>

          <motion.h1
            variants={itemVariants}
            className="text-6xl md:text-8xl lg:text-9xl font-extrabold font-outfit tracking-tight leading-[0.92] mb-6 prime-gradient-text pb-2"
          >
            Wealth tracking <br /> without limits.
          </motion.h1>

          <motion.p
            variants={itemVariants}
            className="text-xl md:text-2xl text-slate-600 dark:text-gray-300 max-w-3xl mx-auto font-medium leading-relaxed"
          >
            A premium, high-frequency dashboard designed for global portfolios.
            Aggregate every asset, every liability, in every currency with glass clarity.
          </motion.p>

          <motion.div variants={itemVariants} className="mt-10 flex gap-4 justify-center flex-wrap">
            <button
              onClick={authed ? () => router.push("/portfolio") : () => setIsLoginOpen(true)}
              className="px-9 py-4.5 rounded-full bg-indigo-600 hover:bg-indigo-700 dark:bg-white dark:text-black dark:hover:bg-slate-100 text-white font-bold text-base md:text-lg hover:scale-105 active:scale-95 transition-all flex items-center gap-2.5 shadow-lg shadow-indigo-500/25 dark:shadow-[0_0_20px_rgba(255,255,255,0.3)] z-20 cursor-pointer"
            >
              Get Started <ArrowRight className="w-5 h-5" />
            </button>
            <button
              onClick={() => setIsAddAssetOpen(true)}
              className="px-9 py-4.5 rounded-full glass-surface font-bold text-base md:text-lg text-slate-800 dark:text-white hover:bg-slate-200/60 dark:hover:bg-white/10 transition-all flex items-center gap-2 glass-border z-20 cursor-pointer"
            >
              + Add Manual Asset
            </button>
          </motion.div>
        </motion.div>

        {/* Dashboard Preview Section */}
        <motion.div
          className="w-full max-w-5xl mt-12 mb-20 relative z-10"
          variants={itemVariants}
        >
          {/* Glass Panel */}
          <div className="glass-surface rounded-3xl p-1.5 border border-slate-200/90 dark:border-white/10 shadow-2xl backdrop-blur-3xl relative overflow-hidden">
            {/* Inner Glow */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-1 bg-indigo-500/20 dark:bg-white/20 blur-md pointer-events-none" />

            <div className="bg-white/90 dark:bg-[#0a0f1e]/85 p-6 md:p-10 rounded-[22px] overflow-hidden">
              <div className="flex flex-col md:flex-row gap-8">
                {/* Stats Column */}
                <div className="flex flex-col gap-4 w-full md:w-5/12">
                  <div className="flex items-center gap-3 mb-1">
                    <div className="w-9 h-9 rounded-xl bg-indigo-500/15 flex items-center justify-center">
                      <Wallet className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                    </div>
                    <span className="text-base font-semibold text-slate-500 dark:text-gray-300 uppercase tracking-wider">Net Worth</span>
                  </div>
                  <div className="text-5xl md:text-6xl font-extrabold font-outfit text-slate-900 dark:text-white tracking-tight">$1,245,390</div>
                  <div className="text-base text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1.5">
                    <span className="px-2 py-0.5 rounded-md bg-emerald-500/15 border border-emerald-500/25 text-xs font-bold">+12.5%</span>
                    <span className="text-slate-500 dark:text-gray-400 font-normal">vs last month</span>
                  </div>

                  <div className="grid grid-cols-1 gap-3.5 mt-4">
                    <StatCard
                      label="Crypto Assets"
                      value="$450,231"
                      icon={Zap}
                      trend="+5.2%"
                      trendUp={true}
                      delay={100}
                    />
                    <StatCard
                      label="Stock Portfolio"
                      value="$689,120"
                      icon={BarChart3}
                      trend="-1.4%"
                      trendUp={false}
                      delay={200}
                    />

                    <button
                      onClick={() => setIsAddAssetOpen(true)}
                      className="w-full py-4 rounded-xl border-2 border-dashed border-slate-300 dark:border-white/10 text-slate-600 dark:text-gray-400 font-semibold text-base flex items-center justify-center gap-2.5 hover:bg-slate-100/80 dark:hover:bg-white/5 hover:border-indigo-500 dark:hover:border-white/20 hover:text-indigo-600 dark:hover:text-white transition-all group cursor-pointer"
                    >
                      <div className="w-8 h-8 rounded-full bg-slate-200/80 dark:bg-white/5 flex items-center justify-center group-hover:bg-indigo-500/15 dark:group-hover:bg-white/10 transition-colors text-slate-600 dark:text-gray-300 group-hover:text-indigo-600 dark:group-hover:text-white">
                        <Plus className="w-5 h-5" />
                      </div>
                      Add Manual Asset
                    </button>
                  </div>
                </div>

                {/* Chart Column */}
                <div className="w-full md:w-7/12 min-h-[340px] relative rounded-2xl bg-slate-50/90 dark:bg-white/5 border border-slate-200/80 dark:border-white/5 overflow-hidden p-6 flex flex-col justify-between">
                  <div className="flex justify-between items-center mb-6 px-1">
                    <div>
                      <h3 className="text-base md:text-lg font-bold text-slate-800 dark:text-gray-200">Portfolio Trajectory</h3>
                      <p className="text-xs md:text-sm text-slate-500 dark:text-gray-400">All connected and manual accounts</p>
                    </div>
                    <div className="flex gap-1.5 p-1 rounded-xl bg-slate-200/70 dark:bg-white/10 border border-slate-300/60 dark:border-white/10">
                      <span className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 text-white cursor-pointer shadow-sm">6M</span>
                      <span className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white cursor-pointer transition-colors">1Y</span>
                      <span className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white cursor-pointer transition-colors">ALL</span>
                    </div>
                  </div>
                  <PortfolioChart />
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full mt-8">
          {[
            {
              icon: BarChart3,
              title: "Unified Hub",
              desc: "Consolidate stocks, crypto, real estate, and traditional accounts into one clear, glass-pane view.",
              color: "text-blue-500 dark:text-blue-400",
              bg: "bg-blue-500/10 dark:bg-white/5"
            },
            {
              icon: Globe,
              title: "Multi-Currency",
              desc: "Real-time conversion across MYR, INR, USD, and SGD with regional smart formatting and precision.",
              color: "text-indigo-500 dark:text-indigo-400",
              bg: "bg-indigo-500/10 dark:bg-white/5"
            },
            {
              icon: ShieldCheck,
              title: "Family Privacy",
              desc: "Share your net worth roadmap with loved ones while maintaining granular control over sensitive data.",
              color: "text-purple-500 dark:text-purple-400",
              bg: "bg-purple-500/10 dark:bg-white/5"
            }
          ].map((item, i) => (
            <motion.div
              key={i}
              className="glass-surface p-8 rounded-3xl flex flex-col items-start gap-4 transition-all duration-500 hover:-translate-y-2 glass-border group"
              variants={itemVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
            >
              <div className={cn("p-4 rounded-2xl transition-colors", item.bg, item.color)}>
                <item.icon className="w-7 h-7" />
              </div>
              <h3 className="text-2xl font-bold font-outfit text-slate-900 dark:text-white">{item.title}</h3>
              <p className="text-base text-slate-600 dark:text-gray-400 leading-relaxed font-medium">{item.desc}</p>
            </motion.div>
          ))}
        </div>
      </main>

      <footer className="mt-24 pb-12 w-full max-w-6xl border-t border-slate-200 dark:border-white/5 pt-12 flex flex-col md:flex-row justify-between items-center gap-8">
        <div className="flex flex-col gap-2 text-center md:text-left">
          <div className="text-2xl font-extrabold font-outfit tracking-tighter prime-gradient-text">FINFLOW</div>
          <p className="text-sm text-slate-500 dark:text-gray-400">The next generation of financial intelligence.</p>
        </div>
        <div className="flex gap-8 text-sm font-semibold text-slate-600 dark:text-gray-400">
          <a href="#" className="hover:text-indigo-600 dark:hover:text-white transition-colors">Privacy Policy</a>
          <a href="#" className="hover:text-indigo-600 dark:hover:text-white transition-colors">Terms of Service</a>
          <a href="#" className="hover:text-indigo-600 dark:hover:text-white transition-colors">Changelog</a>
        </div>
        <div className="text-sm text-slate-500 dark:text-gray-600 font-mono italic">
          v2.0.4-prime_stable
        </div>
      </footer>

      {/* Asset Form Modal */}
      <AddAssetForm isOpen={isAddAssetOpen} onClose={() => setIsAddAssetOpen(false)} />
      <BrokerSettings isOpen={isBrokerOpen} onClose={() => setIsBrokerOpen(false)} />
      <LoginModal isOpen={isLoginOpen} onClose={() => setIsLoginOpen(false)} onAuthed={() => setAuthed(true)} />
    </div>
  );
}
