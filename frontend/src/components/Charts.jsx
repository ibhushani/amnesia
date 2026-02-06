'use client';

import {
    LineChart,
    Line,
    AreaChart,
    Area,
    BarChart,
    Bar,
    PieChart,
    Pie,
    Cell,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts';

const COLORS = {
    primary: '#6366f1',
    secondary: '#a855f7',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#3b82f6',
};

const tooltipStyle = {
    backgroundColor: '#1e293b',
    border: '1px solid rgba(99, 102, 241, 0.3)',
    borderRadius: '8px',
    color: '#f1f5f9',
};

export function ShardOverviewChart({ data }) {
    const chartData = data?.length > 0 ? data : [
        { name: 'Shard 0', samples: 3200, accuracy: 94.2 },
        { name: 'Shard 1', samples: 3150, accuracy: 93.8 },
        { name: 'Shard 2', samples: 3180, accuracy: 94.5 },
        { name: 'Shard 3', samples: 3120, accuracy: 93.1 },
    ];

    return (
        <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(99, 102, 241, 0.1)" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend />
                <Bar dataKey="samples" fill={COLORS.primary} name="Samples" radius={[4, 4, 0, 0]} />
                <Bar dataKey="accuracy" fill={COLORS.secondary} name="Accuracy %" radius={[4, 4, 0, 0]} />
            </BarChart>
        </ResponsiveContainer>
    );
}

export function LossChart({ data }) {
    const chartData = data?.length > 0 ? data : [
        { epoch: 0, forget: 2.5, retain: 0.3, total: 25.3 },
        { epoch: 10, forget: 2.0, retain: 0.32, total: 20.3 },
        { epoch: 20, forget: 1.5, retain: 0.31, total: 15.4 },
        { epoch: 30, forget: 1.1, retain: 0.30, total: 11.2 },
        { epoch: 40, forget: 0.8, retain: 0.29, total: 8.1 },
        { epoch: 50, forget: 0.5, retain: 0.28, total: 5.3 },
        { epoch: 60, forget: 0.35, retain: 0.27, total: 3.8 },
    ];

    return (
        <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(99, 102, 241, 0.1)" />
                <XAxis dataKey="epoch" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend />
                <Line
                    type="monotone"
                    dataKey="forget"
                    stroke={COLORS.danger}
                    strokeWidth={2}
                    name="Forget Loss"
                    dot={false}
                />
                <Line
                    type="monotone"
                    dataKey="retain"
                    stroke={COLORS.success}
                    strokeWidth={2}
                    name="Retain Loss"
                    dot={false}
                />
                <Line
                    type="monotone"
                    dataKey="total"
                    stroke={COLORS.primary}
                    strokeWidth={2}
                    name="Total Loss"
                    dot={false}
                />
            </LineChart>
        </ResponsiveContainer>
    );
}

export function ConfidenceGauge({ confidence, threshold }) {
    const isCompliant = confidence < threshold;
    const data = [
        { name: 'Confidence', value: confidence * 100 },
        { name: 'Remaining', value: (1 - confidence) * 100 },
    ];

    return (
        <div style={{ textAlign: 'center' }}>
            <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                    <Pie
                        data={data}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        startAngle={180}
                        endAngle={0}
                        dataKey="value"
                    >
                        <Cell fill={isCompliant ? COLORS.success : COLORS.danger} />
                        <Cell fill="#1e293b" />
                    </Pie>
                </PieChart>
            </ResponsiveContainer>
            <div style={{ marginTop: '-60px' }}>
                <p style={{
                    fontSize: '2rem',
                    fontWeight: 700,
                    color: isCompliant ? COLORS.success : COLORS.danger
                }}>
                    {(confidence * 100).toFixed(1)}%
                </p>
                <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>
                    Threshold: {(threshold * 100).toFixed(0)}%
                </p>
                <p style={{
                    marginTop: '8px',
                    color: isCompliant ? COLORS.success : COLORS.danger,
                    fontWeight: 600,
                }}>
                    {isCompliant ? '✅ COMPLIANT' : '⚠️ NON-COMPLIANT'}
                </p>
            </div>
        </div>
    );
}

export function TrainingProgressChart({ data }) {
    const chartData = data?.length > 0 ? data : [
        { epoch: 0, loss: 2.3, accuracy: 10 },
        { epoch: 5, loss: 1.8, accuracy: 35 },
        { epoch: 10, loss: 1.2, accuracy: 55 },
        { epoch: 15, loss: 0.8, accuracy: 72 },
        { epoch: 20, loss: 0.5, accuracy: 85 },
        { epoch: 25, loss: 0.35, accuracy: 91 },
        { epoch: 30, loss: 0.25, accuracy: 94 },
    ];

    return (
        <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData}>
                <defs>
                    <linearGradient id="colorAccuracy" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.8} />
                        <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0.1} />
                    </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(99, 102, 241, 0.1)" />
                <XAxis dataKey="epoch" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend />
                <Area
                    type="monotone"
                    dataKey="accuracy"
                    stroke={COLORS.primary}
                    fillOpacity={1}
                    fill="url(#colorAccuracy)"
                    name="Accuracy %"
                />
            </AreaChart>
        </ResponsiveContainer>
    );
}
