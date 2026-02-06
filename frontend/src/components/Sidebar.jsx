'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Brain, LayoutDashboard, Database, Zap, Trash2, Shield, Settings, LogOut, ChevronRight, PieChart } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

const navItems = [
    { href: '/dashboard', icon: LayoutDashboard, label: 'Overview' },
    { href: '/dashboard/datasets', icon: Database, label: 'Datasets' },
    { href: '/dashboard/training', icon: Zap, label: 'Training' },
    { href: '/dashboard/unlearning', icon: Trash2, label: 'Unlearning' },
    { href: '/dashboard/verification', icon: Shield, label: 'Verification' },
];

const sysItems = [
    { href: '/dashboard/system', icon: Settings, label: 'System' },
    { href: '/dashboard/usage', icon: PieChart, label: 'Usage & Billing' },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="w-72 h-screen bg-[#050505] border-r border-white/5 flex flex-col fixed top-0 left-0 z-40">
            {/* Logo */}
            <div className="p-6 pb-8">
                <Link href="/" className="flex items-center gap-3 group">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-900/20 group-hover:shadow-emerald-900/40 transition-shadow">
                        <Brain className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex flex-col">
                        <span className="text-base font-semibold text-white tracking-tight">Amnesia</span>
                        <span className="text-[10px] text-gray-500 uppercase tracking-widest font-medium">Enterprise</span>
                    </div>
                </Link>
            </div>

            {/* Navigation */}
            <div className="flex-1 overflow-y-auto px-4 space-y-8 no-scrollbar">
                {/* Main Nav */}
                <div>
                    <div className="text-[11px] font-medium text-gray-500 uppercase tracking-wider px-3 mb-3">
                        Platform
                    </div>
                    <ul className="space-y-1">
                        {navItems.map((item) => (
                            <NavItem key={item.href} item={item} pathname={pathname} />
                        ))}
                    </ul>
                </div>

                {/* System Nav */}
                <div>
                    <div className="text-[11px] font-medium text-gray-500 uppercase tracking-wider px-3 mb-3">
                        Configuration
                    </div>
                    <ul className="space-y-1">
                        {sysItems.map((item) => (
                            <NavItem key={item.href} item={item} pathname={pathname} />
                        ))}
                    </ul>
                </div>
            </div>

            {/* User Profile */}
            <div className="p-4 m-4 rounded-xl bg-white/5 border border-white/5">
                <div className="flex items-center gap-3 mb-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-gray-700 to-gray-600 border border-white/10" />
                    <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-white truncate">Bhushan Sharma</div>
                        <div className="text-xs text-gray-500 truncate">Admin Workspace</div>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-[10px] text-emerald-400 font-medium">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                        Online
                    </div>
                    <Link
                        href="/login"
                        className="ml-auto p-1.5 text-gray-400 hover:text-white hover:bg-white/10 rounded-md transition-colors"
                    >
                        <LogOut className="w-3.5 h-3.5" />
                    </Link>
                </div>
            </div>
        </aside>
    );
}

function NavItem({ item, pathname }) {
    const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname?.startsWith(item.href));
    const Icon = item.icon;

    return (
        <li>
            <Link
                href={item.href}
                className={cn(
                    "group relative flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-200",
                    isActive
                        ? "text-white"
                        : "text-gray-400 hover:text-white hover:bg-white/5"
                )}
            >
                {isActive && (
                    <motion.div
                        layoutId="activeNav"
                        className="absolute inset-0 bg-white/5 rounded-lg border border-white/5"
                        initial={false}
                        transition={{ type: "spring", stiffness: 400, damping: 30 }}
                    />
                )}
                <Icon className={cn("w-4 h-4 relative z-10 transition-colors", isActive ? "text-emerald-400" : "text-gray-500 group-hover:text-gray-300")} />
                <span className="relative z-10 font-medium">{item.label}</span>
                {isActive && <ChevronRight className="w-3 h-3 ml-auto text-emerald-500/50" />}
            </Link>
        </li>
    );
}
