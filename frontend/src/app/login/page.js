'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Brain, ArrowRight } from 'lucide-react';

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        setLoading(true);
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 1000);
    };

    return (
        <div className="min-h-screen bg-[#0a0a0a] flex">
            {/* Left - Form */}
            <div className="flex-1 flex items-center justify-center px-8">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="w-full max-w-md"
                >
                    <Link href="/landing" className="flex items-center gap-3 mb-12">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center">
                            <Brain className="w-6 h-6 text-black" />
                        </div>
                        <span className="text-xl font-semibold text-white">Amnesia</span>
                    </Link>

                    <h1 className="text-3xl font-bold text-white mb-2">Welcome back</h1>
                    <p className="text-gray-400 mb-8">Sign in to your account</p>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="you@company.com"
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••"
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition"
                            />
                        </div>

                        <div className="flex items-center justify-between">
                            <label className="flex items-center gap-2 text-sm text-gray-400">
                                <input type="checkbox" className="rounded bg-white/5 border-white/10" />
                                Remember me
                            </label>
                            <a href="#" className="text-sm text-emerald-400 hover:text-emerald-300">Forgot password?</a>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-3 bg-gradient-to-r from-emerald-500 to-cyan-500 text-black font-medium rounded-lg flex items-center justify-center gap-2 hover:opacity-90 transition disabled:opacity-50"
                        >
                            {loading ? 'Signing in...' : 'Sign In'}
                            {!loading && <ArrowRight className="w-4 h-4" />}
                        </button>
                    </form>

                    <div className="mt-8 text-center text-gray-400">
                        Don't have an account?{' '}
                        <Link href="/signup" className="text-emerald-400 hover:text-emerald-300">Sign up</Link>
                    </div>
                </motion.div>
            </div>

            {/* Right - Gradient */}
            <div className="hidden lg:block flex-1 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/20 via-cyan-500/10 to-transparent" />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
                    <div className="text-4xl font-bold text-white mb-4">The Right to Be Forgotten</div>
                    <div className="text-gray-400">GDPR-compliant machine unlearning</div>
                </div>
            </div>
        </div>
    );
}
