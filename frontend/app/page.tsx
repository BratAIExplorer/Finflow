"use client";

import { motion, Variants } from "framer-motion";
import { ArrowRight, BarChart3, Wallet, ShieldCheck, Globe, Zap, Plus } from "lucide-react";
import { cn } from "@/lib/utils";
import { StatCard } from "@/components/ui/StatCard";
import { PortfolioChart } from "@/components/ui/PortfolioChart";
import { AddAssetForm } from "@/components/AddAssetForm";
import { BrokerSettings } from "@/components/BrokerSettings";
import { HoldingsDashboard } from "@/components/HoldingsDashboard";
import { LoginModal, TOKEN_KEY } from "@/components/LoginModal";
import { useEffect, useState } from "react";

export default function Home() {
  const [isAddAssetOpen, setIsAddAssetOpen] = useState(false);
  const [isBrokerOpen, setIsBrokerOpen] = useState(false);
  const [isHoldingsOpen, setIsHoldingsOpen] = useState(false);
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
    <div className="min-h-screen bg-[#030712] text-white flex flex-col items-center justify-center p-6 md:p-12 relative overflow-hidden font-inter selection:bg-indigo-500/30">
      {/* Dynamic Background Orbs */}
      <div className="bg-prime-orb top-[-10%] left-[-5%] w-[600px] h-[600px] bg-indigo-600/30 blur-[120px]" />
      <div className="bg-prime-orb bottom-[-15%] right-[-5%] w-[500px] h-[500px] bg-blue-600/20 blur-[100px]" />
      <div className="bg-prime-orb top-[20%] right-[10%] w-[300px] h-[300px] bg-purple-600/10 blur-[80px]" />

      {/* Navigation - Glass Overlay */}
      <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-full max-w-lg px-4">
        <div className="glass-surface py-3 px-6 rounded-full flex items-center justify-between glass-border shadow-2xl">
          <div className="text-xl font-bold font-outfit tracking-tighter prime-gradient-text">FINFLOW</div>
          <div className="flex gap-5 text-sm font-medium text-gray-400">
            <button onClick={requireAuth(() => setIsHoldingsOpen(true))} className="hover:text-white transition-colors">Portfolio</button>
            <button onClick={requireAuth(() => setIsBrokerOpen(true))} className="hover:text-white transition-colors">Plugins</button>
            <a href="#" className="hover:text-white transition-colors">Family</a>
            {authed ? (
              <button onClick={signOut} className="hover:text-white transition-colors">Sign out</button>
            ) : (
              <button onClick={() => setIsLoginOpen(true)} className="text-indigo-300 hover:text-white transition-colors">Sign in</button>
            )}
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
          <motion.div variants={itemVariants} className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-surface mb-8 glass-border">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            <span className="text-[10px] uppercase tracking-widest font-bold text-blue-200">Connectors Online</span>
          </motion.div>

          <motion.h1
            variants={itemVariants}
            className="text-6xl md:text-8xl font-bold font-outfit tracking-tight leading-[0.9] mb-6 prime-gradient-text pb-2"
          >
            Wealth tracking <br /> without limits.
          </motion.h1>

          <motion.p
            variants={itemVariants}
            className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto font-medium"
          >
            A premium, high-frequency dashboard designed for global portfolios.
            Aggregate every asset, every liability, in every currency.
          </motion.p>

          <motion.div variants={itemVariants} className="mt-10 flex gap-4 justify-center">
            <button
              onClick={authed ? () => setIsHoldingsOpen(true) : () => setIsLoginOpen(true)}
              className="px-8 py-4 rounded-full bg-white text-black font-bold text-sm hover:scale-105 active:scale-95 transition-all flex items-center gap-2 shadow-[0_0_20px_rgba(255,255,255,0.3)] z-20 cursor-pointer"
            >
              Get Started <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => alert("Demo Mode: Visualize your wealth in glass.")}
              className="px-8 py-4 rounded-full glass-surface font-bold text-sm hover:bg-white/10 transition-all flex items-center gap-2 glass-border z-20 cursor-pointer"
            >
              View Demo
            </button>
          </motion.div>
        </motion.div>

        {/* Dashboard Preview Section */}
        <motion.div
          className="w-full max-w-5xl mt-20 mb-20 relative z-10"
          variants={itemVariants}
        >
          {/* Glass Panel */}
          <div className="glass-surface rounded-3xl p-1 border border-white/10 shadow-2xl backdrop-blur-3xl relative overflow-hidden">
            {/* Inner Glow */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-1 bg-white/20 blur-md pointer-events-none" />

            <div className="bg-[#0a0f1e]/80 p-6 md:p-8 rounded-[20px] overflow-hidden">
              <div className="flex flex-col md:flex-row gap-8">
                {/* Stats Column */}
                <div className="flex flex-col gap-4 w-full md:w-1/3">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center">
                      <Wallet className="w-4 h-4 text-indigo-400" />
                    </div>
                    <span className="text-sm font-semibold text-gray-300">Net Worth</span>
                  </div>
                  <div className="text-4xl font-bold font-outfit text-white tracking-tight">$1,245,390</div>
                  <div className="text-sm text-emerald-400 font-medium flex items-center gap-1">
                    +12.5% <span className="text-gray-500">vs last month</span>
                  </div>

                  <div className="grid grid-cols-1 gap-3 mt-4">
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
                      className="w-full py-4 rounded-xl border-2 border-dashed border-white/10 text-gray-400 font-medium text-sm flex items-center justify-center gap-2 hover:bg-white/5 hover:border-white/20 hover:text-white transition-all group"
                    >
                      <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-white/10 transition-colors">
                        <Plus className="w-4 h-4" />
                      </div>
                      Add Manual Asset
                    </button>
                  </div>
                </div>

                {/* Chart Column */}
                <div className="w-full md:w-2/3 min-h-[300px] relative rounded-2xl bg-white/5 border border-white/5 overflow-hidden p-4">
                  <div className="flex justify-between items-center mb-6 px-2">
                    <h3 className="text-sm font-semibold text-gray-400">Portfolio Growth</h3>
                    <div className="flex gap-2">
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-white/10 text-white cursor-pointer">6M</span>
                      <span className="px-3 py-1 rounded-full text-xs font-medium text-gray-500 hover:text-white cursor-pointer transition-colors">1Y</span>
                      <span className="px-3 py-1 rounded-full text-xs font-medium text-gray-500 hover:text-white cursor-pointer transition-colors">ALL</span>
                    </div>
                  </div>
                  <PortfolioChart />
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full mt-12">
          {[
            {
              icon: BarChart3,
              title: "Unified Hub",
              desc: "Consolidate stocks, crypto, and traditional assets into one beautiful, glass-pane view.",
              color: "text-blue-400"
            },
            {
              icon: Globe,
              title: "Multi-Currency",
              desc: "Real-time conversion across MYR, INR, USD, and SGD with regional smart formatting.",
              color: "text-indigo-400"
            },
            {
              icon: ShieldCheck,
              title: "Family Privacy",
              desc: "Share your net worth with loved ones while maintaining granular control over sensitive data.",
              color: "text-purple-400"
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
              <div className={cn("p-4 rounded-2xl bg-white/5 group-hover:bg-white/10 transition-colors", item.color)}>
                <item.icon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold font-outfit">{item.title}</h3>
              <p className="text-sm text-gray-500 leading-relaxed font-medium">{item.desc}</p>
            </motion.div>
          ))}
        </div>
      </main>

      <footer className="mt-24 pb-12 w-full max-w-6xl border-t border-white/5 pt-12 flex flex-col md:flex-row justify-between items-center gap-8">
        <div className="flex flex-col gap-2">
          <div className="text-xl font-bold font-outfit tracking-tighter prime-gradient-text">FINFLOW</div>
          <p className="text-xs text-gray-600">The next generation of financial intelligence.</p>
        </div>
        <div className="flex gap-8 text-xs font-semibold text-gray-500">
          <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
          <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
          <a href="#" className="hover:text-white transition-colors">Changelog</a>
        </div>
        <div className="text-xs text-gray-700 font-mono italic">
          v2.0.4-prime_stable
        </div>
      </footer>

      {/* Asset Form Modal */}
      <AddAssetForm isOpen={isAddAssetOpen} onClose={() => setIsAddAssetOpen(false)} />
      <BrokerSettings isOpen={isBrokerOpen} onClose={() => setIsBrokerOpen(false)} />
      <HoldingsDashboard isOpen={isHoldingsOpen} onClose={() => setIsHoldingsOpen(false)} />
      <LoginModal isOpen={isLoginOpen} onClose={() => setIsLoginOpen(false)} onAuthed={() => setAuthed(true)} />
    </div>
  );
}
