'use client';

import { motion } from 'framer-motion';
import { usePathname } from 'next/navigation';
import { ArrowRight, Check, X, Upload, FileText } from 'lucide-react';

/**
 * Premium UI Components - Linear/Vercel Style
 */

// Metric Card
export function MetricCard({ value, label, change, changeType, icon: Icon }) {
    return (
        <div className="p-6 rounded-2xl bg-[#0a0a0a] border border-white/5 hover:border-white/10 transition-colors group">
            <div className="flex items-center justify-between mb-4">
                {Icon && (
                    <div className="p-2 rounded-lg bg-white/5 text-gray-400 group-hover:text-white transition-colors">
                        <Icon className="w-5 h-5" />
                    </div>
                )}
                {change && (
                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${changeType === 'positive' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                        }`}>
                        {changeType === 'positive' ? '+' : ''}{change}
                    </span>
                )}
            </div>
            <div className="text-3xl font-bold text-white mb-1 tracking-tight">{value}</div>
            <div className="text-sm text-gray-500 font-medium">{label}</div>
        </div>
    );
}

// Card Container
export function Card({ title, children, className = '', style = {} }) {
    return (
        <div className={`p-6 rounded-2xl bg-[#0a0a0a] border border-white/5 ${className}`} style={style}>
            {title && <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>}
            {children}
        </div>
    );
}

// Status Badge
export function Badge({ status, variant = 'neutral' }) {
    const variants = {
        success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
        warning: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
        danger: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
        neutral: 'bg-white/5 text-gray-400 border-white/10',
    };

    return (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${variants[variant]}`}>
            {status}
        </span>
    );
}

// Button
export function Button({
    children,
    variant = 'primary',
    fullWidth = false,
    disabled = false,
    onClick,
    type = 'button',
    icon: Icon,
    className = '',
    style = {},
    ...props
}) {
    const baseClass = "inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed";

    const variants = {
        primary: "bg-white text-black hover:bg-gray-200",
        secondary: "bg-white/5 text-white border border-white/10 hover:bg-white/10",
        danger: "bg-rose-500/10 text-rose-400 border border-rose-500/20 hover:bg-rose-500/20",
        ghost: "text-gray-400 hover:text-white hover:bg-white/5",
    };

    return (
        <button
            type={type}
            className={`${baseClass} ${variants[variant]} ${fullWidth ? 'w-full' : ''} ${className}`}
            style={style}
            disabled={disabled}
            onClick={onClick}
            {...props}
        >
            {children}
            {Icon && <Icon className="w-4 h-4" />}
        </button>
    );
}

// Form Group
export function FormGroup({ label, hint, children }) {
    return (
        <div className="space-y-2 mb-4">
            {label && <label className="block text-sm font-medium text-gray-400">{label}</label>}
            {children}
            {hint && <p className="text-xs text-gray-500">{hint}</p>}
        </div>
    );
}

// Input
export function Input({ className = '', ...props }) {
    return (
        <input
            className={`w-full px-3 py-2 bg-[#050505] border border-white/10 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all ${className}`}
            {...props}
        />
    );
}

// Progress Bar
export function ProgressBar({ progress }) {
    return (
        <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
                transition={{ duration: 0.5 }}
                className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500"
            />
        </div>
    );
}

// Alert/Message Box
export function Alert({ type = 'info', children }) {
    const styles = {
        info: 'bg-blue-500/10 border-blue-500/20 text-blue-400',
        success: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
        warning: 'bg-amber-500/10 border-amber-500/20 text-amber-400',
        danger: 'bg-rose-500/10 border-rose-500/20 text-rose-400',
    };

    return (
        <div className={`p-4 mb-4 rounded-lg border flex items-start gap-3 ${styles[type]}`}>
            <div className="mt-0.5">
                {type === 'success' && <Check className="w-4 h-4" />}
                {type === 'danger' && <X className="w-4 h-4" />}
            </div>
            <div className="text-sm">{children}</div>
        </div>
    );
}

// Slider
export function Slider({ value, onChange, min = 0, max = 100, step = 1 }) {
    return (
        <div className="relative flex items-center w-full h-10">
            <input
                type="range"
                min={min}
                max={max}
                step={step}
                value={value}
                onChange={(e) => onChange(parseFloat(e.target.value))}
                className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-emerald-500 hover:accent-emerald-400"
            />
            {/* Custom styling via CSS module or global CSS is preferred for range, but basic accent-color works well in modern browsers */}
        </div>
    );
}

// Upload Zone
export function UploadZone({ onFileSelect, accept = '.csv', hint }) {
    const handleDrop = (e) => {
        e.preventDefault();
        const file = e.dataTransfer?.files?.[0];
        if (file) onFileSelect(file);
    };

    const handleChange = (e) => {
        const file = e.target.files?.[0];
        if (file) onFileSelect(file);
    };

    return (
        <label
            className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-white/10 rounded-2xl bg-white/[0.02] hover:bg-white/[0.05] hover:border-emerald-500/30 transition-all cursor-pointer group"
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
        >
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <div className="w-12 h-12 rounded-full bg-white/5 border border-white/5 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <Upload className="w-6 h-6 text-gray-400 group-hover:text-emerald-400 transition-colors" />
                </div>
                <p className="mb-2 text-sm text-gray-400">
                    <span className="font-semibold text-white">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-gray-500">{accept} files</p>
                {hint && <p className="mt-4 text-xs text-gray-600 max-w-xs text-center">{hint}</p>}
            </div>
            <input
                type="file"
                className="hidden"
                accept={accept}
                onChange={handleChange}
            />
        </label>
    );
}

// Data Table
export function DataTable({ columns, data }) {
    if (!data || data.length === 0) {
        return (
            <div className="text-center py-12 text-gray-500">
                No data available
            </div>
        );
    }

    return (
        <div className="w-full overflow-x-auto">
            <table className="w-full text-sm text-left text-gray-400">
                <thead className="text-xs text-gray-500 uppercase bg-white/5 border-b border-white/5">
                    <tr>
                        {columns.map((col) => (
                            <th key={col.key} className="px-6 py-3 font-medium">
                                {col.label}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, idx) => (
                        <tr key={idx} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                            {columns.map((col) => (
                                <td key={col.key} className="px-6 py-4 whitespace-nowrap">
                                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

// Gauge (Verification)
export function Gauge({ value, label, threshold }) {
    const isPass = value < threshold;
    const color = isPass ? 'text-emerald-400' : 'text-rose-400';
    const percent = Math.min(100, Math.max(0, value * 100));

    // Simple SVG gauge
    return (
        <div className="flex flex-col items-center justify-center py-6">
            <div className="relative w-48 h-24 overflow-hidden mb-4">
                <div className="absolute top-0 left-0 w-full h-48 rounded-full border-[12px] border-white/5 border-b-0 box-border" />
                <div
                    className={`absolute top-0 left-0 w-full h-48 rounded-full border-[12px] border-b-0 box-border transition-all duration-1000 ${isPass ? 'border-emerald-500' : 'border-rose-500'}`}
                    style={{
                        transform: `rotate(${percent * 1.8 - 180}deg)`,
                        transformOrigin: '50% 100%',
                        clipPath: 'polygon(0 0, 100% 0, 100% 50%, 0 50%)'
                    }}
                />
            </div>
            <div className={`text-4xl font-bold ${color} mb-1`}>{(value * 100).toFixed(1)}%</div>
            <div className="text-sm text-gray-500">{label}</div>

            <div className="mt-4 flex gap-4 text-xs text-gray-500">
                <div className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded-full bg-emerald-500" />
                    &lt; {(threshold * 100).toFixed(0)}% (Pass)
                </div>
                <div className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded-full bg-rose-500" />
                    &gt; {(threshold * 100).toFixed(0)}% (Fail)
                </div>
            </div>
        </div>
    );
}
