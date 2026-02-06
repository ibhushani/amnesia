'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Database, Zap, Trash2, Shield, Activity, FileCheck, Search, Bell } from 'lucide-react';
import api from '@/lib/api';

export default function DashboardPage() {
    const [isOnline, setIsOnline] = useState(false);
    const [greeting, setGreeting] = useState('');

    useEffect(() => {
        const hour = new Date().getHours();
        if (hour < 12) setGreeting('Good morning');
        else if (hour < 18) setGreeting('Good afternoon');
        else setGreeting('Good evening');

        // Initial check
        checkStatus();
    }, []);

    const checkStatus = async () => {
        try {
            const health = await api.healthCheck();
            setIsOnline(health.success);
        } catch (e) {
            setIsOnline(false);
        }
    };

    const stats = [
        { label: 'Active Shards', value: '4', icon: Activity, trend: '+12%', trendUp: true },
        { label: 'Samples Processed', value: '10,240', icon: Database, trend: '+8.5%', trendUp: true },
        { label: 'Data Unlearned', value: '127', icon: Trash2, trend: '-2.1%', trendUp: false },
        { label: 'Certificates Issued', value: '12', icon: FileCheck, trend: '100%', trendUp: true },
    ];

    const actions = [
        {
            title: 'Upload Dataset',
            description: 'Import CSV data to training pipeline',
            href: '/dashboard/datasets',
            icon: Database,
            color: 'emerald'
        },
        {
            title: 'Start Training',
            description: 'Launch SISA distributed training',
            href: '/dashboard/training',
            icon: Zap,
            color: 'amber'
        },
        {
            title: 'New Unlearning Request',
            description: 'Process deletion for specific IDs',
            href: '/dashboard/unlearning',
            icon: Trash2,
            color: 'rose'
        }
    ];

    return (
        <div className="space-y-12">
            {/* Header Area */}
            <header className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                        {greeting}, Bhushan
                    </h1>
                    <p className="text-gray-500 mt-2">
                        Here's what's happening with your models today.
                    </p>
                </div>
                <div className="flex items-center gap-4">
                    <button className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition">
                        <Search className="w-5 h-5" />
                    </button>
                    <button className="relative p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition">
                        <Bell className="w-5 h-5" />
                        <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-rose-500 border-2 border-[#050505]" />
                    </button>
                </div>
            </header>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((stat, i) => (
                    <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="p-6 rounded-2xl bg-[#0a0a0a] border border-white/5 hover:border-white/10 transition-colors group"
                    >
                        <div className="flex items-center justify-between mb-4">
                            <div className="p-2 rounded-lg bg-white/5 text-gray-400 group-hover:text-white transition-colors">
                                <stat.icon className="w-5 h-5" />
                            </div>
                            <span className={`text-xs font-medium px-2 py-1 rounded-full ${stat.trendUp ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                                }`}>
                                {stat.trend}
                            </span>
                        </div>
                        <div className="text-3xl font-bold text-white mb-1">{stat.value}</div>
                        <div className="text-sm text-gray-500">{stat.label}</div>
                    </motion.div>
                ))}
            </div>

            {/* Quick Actions */}
            <section>
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold">Quick Actions</h2>
                </div>
                <div className="grid md:grid-cols-3 gap-6">
                    {actions.map((action, i) => (
                        <motion.div
                            key={action.title}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 + i * 0.1 }}
                        >
                            <Link
                                href={action.href}
                                className="group relative block p-6 rounded-2xl bg-[#0a0a0a] border border-white/5 hover:border-white/10 transition-all duration-300 hover:shadow-2xl hover:shadow-emerald-900/5 hover:-translate-y-1"
                            >
                                <div className="absolute top-6 right-6 opacity-0 group-hover:opacity-100 transition-opacity transform group-hover:translate-x-1">
                                    <ArrowRight className="w-5 h-5 text-gray-400" />
                                </div>
                                <div className={`w-12 h-12 rounded-xl bg-${action.color}-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                                    <action.icon className={`w-6 h-6 text-${action.color}-400`} />
                                </div>
                                <h3 className="text-lg font-semibold text-white mb-2">{action.title}</h3>
                                <p className="text-sm text-gray-500 leading-relaxed">
                                    {action.description}
                                </p>
                            </Link>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* Compliance Section */}
            <section className="rounded-3xl border border-white/5 bg-[#0a0a0a] overflow-hidden">
                <div className="p-8 border-b border-white/5 flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-semibold mb-1">Compliance Status</h2>
                        <p className="text-gray-500 text-sm">Real-time regulatory adherence monitoring</p>
                    </div>
                    <div className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                        Audit Ready
                    </div>
                </div>
                <div className="grid md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-white/5">
                    {[
                        { name: 'GDPR Article 17', region: 'European Union', status: 'Compliant' },
                        { name: 'CCPA §1798.105', region: 'California, US', status: 'Compliant' },
                        { name: 'LGPD Article 18', region: 'Brazil', status: 'Compliant' },
                    ].map((reg) => (
                        <div key={reg.name} className="p-8 hover:bg-white/[0.02] transition-colors">
                            <div className="flex items-center gap-3 mb-3">
                                <div className="w-2 h-2 rounded-full bg-emerald-500" />
                                <h3 className="font-medium text-white">{reg.name}</h3>
                            </div>
                            <p className="text-sm text-gray-500 mb-4">{reg.region}</p>
                            <div className="flex items-center gap-2 text-xs font-medium text-emerald-400">
                                <FileCheck className="w-3.5 h-3.5" />
                                {reg.status}
                            </div>
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
}
