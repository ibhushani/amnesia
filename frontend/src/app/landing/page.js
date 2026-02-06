'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion, useScroll, useTransform } from 'framer-motion';
import { ArrowRight, Shield, Zap, FileCheck, Brain, ChevronDown, Github, Twitter, Linkedin, CheckCircle2, Play } from 'lucide-react';

export default function LandingPage() {
    const [scrolled, setScrolled] = useState(false);
    const { scrollY } = useScroll();
    const y1 = useTransform(scrollY, [0, 500], [0, 200]);
    const y2 = useTransform(scrollY, [0, 500], [0, -150]);

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <div className="min-h-screen bg-[#050505] text-white overflow-hidden selection:bg-emerald-500/20">
            {/* Ambient Background */}
            <div className="fixed inset-0 z-0">
                <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-emerald-500/5 blur-[120px] animate-pulse-glow" />
                <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-cyan-500/5 blur-[120px] animate-pulse-glow delay-1000" />
                <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-[0.02]" />
            </div>

            {/* Navigation */}
            <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'bg-[#050505]/80 backdrop-blur-md border-b border-white/5' : 'bg-transparent'
                }`}>
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-3 group">
                        <div className="relative">
                            <div className="absolute inset-0 bg-emerald-500/20 rounded-lg blur-md group-hover:bg-emerald-500/40 transition-all duration-300" />
                            <div className="relative w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center">
                                <Brain className="w-5 h-5 text-white" />
                            </div>
                        </div>
                        <span className="text-lg font-semibold tracking-tight">Amnesia</span>
                    </Link>

                    <div className="hidden md:flex items-center gap-8">
                        {['Features', 'How It Works', 'Pricing', 'API'].map((item) => (
                            <a
                                key={item}
                                href={`#${item.toLowerCase().replace(/ /g, '-')}`}
                                className="text-sm font-medium text-gray-400 hover:text-white transition-colors"
                            >
                                {item}
                            </a>
                        ))}
                    </div>

                    <div className="flex items-center gap-4">
                        <Link href="/login" className="text-sm font-medium text-gray-400 hover:text-white transition-colors">
                            Log In
                        </Link>
                        <Link
                            href="/dashboard"
                            className="group relative px-5 py-2 rounded-full bg-white text-black text-sm font-semibold hover:bg-gray-100 transition-all overflow-hidden"
                        >
                            <span className="relative z-10">Get Started</span>
                            <div className="absolute inset-0 bg-gradient-to-r from-emerald-200 to-cyan-200 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="relative z-10 min-h-screen flex flex-col justify-center items-center px-6 pt-20">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="text-center max-w-5xl mx-auto"
                >
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-emerald-400 mb-8 animate-float">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                        GDPR & CCPA Compliant Unlearning
                    </div>

                    <h1 className="text-6xl md:text-8xl font-bold tracking-tighter mb-8 bg-clip-text text-transparent bg-gradient-to-b from-white to-white/40">
                        Make Your AI <br />
                        <span className="text-gradient">Forget.</span>
                    </h1>

                    <p className="text-xl md:text-2xl text-gray-400 max-w-2xl mx-auto mb-12 leading-relaxed">
                        Surgically remove data from ML models in minutes. <br className="hidden md:block" />
                        Cryptographic proof for compliance, zero retraining required.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <Link
                            href="/dashboard"
                            className="group relative px-8 py-4 rounded-full bg-white text-black font-semibold text-lg hover:shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)] transition-all duration-300"
                        >
                            Start Free Trial
                            <ArrowRight className="inline-block ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </Link>
                        <Link
                            href="#how-it-works"
                            className="px-8 py-4 rounded-full bg-white/5 border border-white/10 text-white font-medium hover:bg-white/10 transition-colors flex items-center gap-2"
                        >
                            <Play className="w-4 h-4 fill-current" />
                            Watch Demo
                        </Link>
                    </div>
                </motion.div>

                {/* Abstract Visuals */}
                <motion.div style={{ y: y1 }} className="absolute left-[10%] top-[30%] -z-10 opacity-20">
                    <DatabaseIcon className="w-64 h-64 text-emerald-500" />
                </motion.div>
                <motion.div style={{ y: y2 }} className="absolute right-[10%] bottom-[20%] -z-10 opacity-20">
                    <ShieldIcon className="w-48 h-48 text-cyan-500" />
                </motion.div>
            </section>

            {/* Features Grid */}
            <section id="features" className="py-32 px-6 relative z-10">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-24">
                        <h2 className="text-3xl md:text-5xl font-bold mb-6">Enterprise-Grade Architecture</h2>
                        <p className="text-gray-400 max-w-xl mx-auto text-lg">
                            Built on SISA (Sharded, Isolated, Sliced, Aggregated) architecture for instant compliance.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-6">
                        <BentoCard
                            title="Instant Unlearning"
                            desc="Forget data points in < 100ms via shard isolation."
                            icon={Zap}
                            color="emerald"
                            colSpan="md:col-span-2"
                        >
                            <div className="absolute right-0 bottom-0 w-64 h-32 bg-gradient-to-t from-emerald-500/10 to-transparent blur-2xl" />
                        </BentoCard>
                        <BentoCard
                            title="Cryptographic Proof"
                            desc="SHA-256 verification logs for every deletion request."
                            icon={Shield}
                            color="cyan"
                        />
                        <BentoCard
                            title="Audit Ready"
                            desc="Automated PDF compliance certificates."
                            icon={FileCheck}
                            color="purple"
                        />
                        <BentoCard
                            title="Zero Performance Loss"
                            desc="Maintain model accuracy while removing specific samples."
                            icon={Brain}
                            color="blue"
                            colSpan="md:col-span-2"
                        />
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section id="how-it-works" className="py-32 px-6 bg-white/[0.02] border-y border-white/5">
                <div className="max-w-7xl mx-auto">
                    <div className="flex flex-col md:flex-row gap-20">
                        <div className="md:w-1/3">
                            <h2 className="text-4xl font-bold mb-6 sticky top-32">How Amnesia Works</h2>
                            <p className="text-gray-400 text-lg sticky top-48">
                                A simple, transparent pipeline that integrates directly into your existing ML/Ops workflow.
                            </p>
                        </div>
                        <div className="md:w-2/3 space-y-20 relative">
                            {/* Connecting Line */}
                            <div className="absolute left-[27px] top-4 bottom-4 w-[2px] bg-gradient-to-b from-emerald-500 via-cyan-500 to-purple-500 md:block hidden opacity-20" />

                            {[
                                { title: 'Sharding & Training', desc: 'Data is partitioned into isolated shards. Each shard trains a sub-model independently.', icon: '01' },
                                { title: 'Unlearning Request', desc: 'When a user requests deletion, we identify the exact shards containing their data.', icon: '02' },
                                { title: 'Targeted Retraining', desc: 'Only affected shards are retrained. 95% of the model remains untouched.', icon: '03' },
                                { title: 'Verification', desc: 'The new model aggregation is verified and a certificate is issued.', icon: '04' }
                            ].map((step, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, x: 50 }}
                                    whileInView={{ opacity: 1, x: 0 }}
                                    viewport={{ once: true, margin: "-100px" }}
                                    className="flex gap-8 relative"
                                >
                                    <div className="flex-shrink-0 w-14 h-14 rounded-full bg-[#0a0a0a] border border-white/10 flex items-center justify-center font-mono text-emerald-500 font-bold z-10">
                                        {step.icon}
                                    </div>
                                    <div className="pt-2">
                                        <h3 className="text-2xl font-semibold mb-3">{step.title}</h3>
                                        <p className="text-gray-400 leading-relaxed text-lg">{step.desc}</p>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* Creator Section */}
            <section className="py-32 px-6 relative z-10">
                <div className="max-w-3xl mx-auto text-center">
                    <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-emerald-500 to-cyan-500 p-[1px] mb-8">
                        <div className="w-full h-full rounded-2xl bg-[#050505] flex items-center justify-center">
                            <Brain className="w-10 h-10 text-emerald-400" />
                        </div>
                    </div>
                    <h2 className="text-4xl font-bold mb-4">Built by Bhushan Sharma</h2>
                    <p className="text-xl text-gray-400 mb-10">
                        Designing the future of privacy-preserving AI.
                    </p>
                    <div className="flex items-center justify-center gap-4">
                        <SocialLink href="https://github.com/ibhushani" icon={Github} label="GitHub" />
                        <SocialLink href="https://www.linkedin.com/in/ibhushani/" icon={Linkedin} label="LinkedIn" />
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 px-6 border-t border-white/5 text-center text-gray-600 text-sm">
                <p>&copy; 2026 Amnesia Inc. All rights reserved.</p>
            </footer>
        </div>
    );
}

// Components
function BentoCard({ title, desc, icon: Icon, color, colSpan = '', children }) {
    const colorClasses = {
        emerald: 'text-emerald-400 group-hover:text-emerald-300',
        cyan: 'text-cyan-400 group-hover:text-cyan-300',
        purple: 'text-purple-400 group-hover:text-purple-300',
        blue: 'text-blue-400 group-hover:text-blue-300',
    };

    return (
        <motion.div
            whileHover={{ y: -5 }}
            className={`group relative overflow-hidden p-8 rounded-3xl bg-[#0a0a0a] border border-white/5 hover:border-white/10 transition-all duration-300 ${colSpan}`}
        >
            <div className="relative z-10">
                <div className={`w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mb-6 transition-colors ${colorClasses[color]}`}>
                    <Icon className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold mb-3">{title}</h3>
                <p className="text-gray-400">{desc}</p>
            </div>
            {children}
        </motion.div>
    );
}

function SocialLink({ href, icon: Icon, label }) {
    return (
        <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 px-6 py-3 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 hover:border-white/10 transition-all group"
        >
            <Icon className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" />
            <span className="font-medium">{label}</span>
        </a>
    );
}

// Decorative Icons
function DatabaseIcon(props) {
    return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" {...props}>
            <ellipse cx="12" cy="5" rx="9" ry="3" />
            <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
            <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
        </svg>
    )
}

function ShieldIcon(props) {
    return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" {...props}>
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
    )
}
