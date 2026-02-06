'use client';

import { useState, useEffect } from 'react';
import { Card, Badge, MetricCard } from '@/components/ui';
import api from '@/lib/api';

export default function SystemPage() {
    const [status, setStatus] = useState({
        api: { online: false },
        db: { online: false },
        redis: { online: false },
    });

    useEffect(() => {
        const checkStatus = async () => {
            const health = await api.healthCheck();
            setStatus(prev => ({
                ...prev,
                api: {
                    online: health.success,
                    version: health.data?.version || '—',
                    architecture: health.data?.architecture || '—',
                },
            }));
        };
        checkStatus();
        const interval = setInterval(checkStatus, 5000);
        return () => clearInterval(interval);
    }, []);

    const services = [
        { name: 'FastAPI Server', port: '8000', status: status.api.online ? 'Running' : 'Stopped' },
        { name: 'PostgreSQL', port: '5432', status: 'Running' },
        { name: 'Redis', port: '6379', status: 'Running' },
        { name: 'Next.js Frontend', port: '3000', status: 'Running' },
    ];

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1>System</h1>
                <p>Monitor infrastructure and service health</p>
            </div>

            <div className="metrics-grid">
                <MetricCard
                    value={status.api.online ? 'Online' : 'Offline'}
                    label="API Status"
                />
                <MetricCard value={status.api.version || '—'} label="Version" />
                <MetricCard value={status.api.architecture || '—'} label="Architecture" />
                <MetricCard value="4" label="Docker Containers" />
            </div>

            <div className="two-columns">
                <Card title="🐳 Services">
                    {services.map((svc) => (
                        <div
                            key={svc.name}
                            style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                padding: '12px 0',
                                borderBottom: '1px solid var(--border-default)',
                            }}
                        >
                            <div>
                                <div style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{svc.name}</div>
                                <div style={{ color: 'var(--text-muted)', fontSize: '12px' }}>Port {svc.port}</div>
                            </div>
                            <Badge
                                status={svc.status}
                                variant={svc.status === 'Running' ? 'success' : 'danger'}
                            />
                        </div>
                    ))}
                </Card>

                <Card title="⚙️ Configuration">
                    <table style={{ width: '100%' }}>
                        <tbody>
                            {[
                                ['Database', 'PostgreSQL 15'],
                                ['Task Queue', 'Redis + Celery'],
                                ['ML Framework', 'PyTorch'],
                                ['GPU', 'CUDA (if available)'],
                            ].map(([key, val]) => (
                                <tr key={key}>
                                    <td style={{ padding: '8px 0', color: 'var(--text-muted)' }}>{key}</td>
                                    <td style={{ padding: '8px 0', color: 'var(--text-primary)', textAlign: 'right' }}>{val}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </Card>
            </div>

            <Card title="📚 API Endpoints" style={{ marginTop: '24px' }}>
                <div style={{ overflowX: 'auto' }}>
                    <table>
                        <thead>
                            <tr>
                                <th>Endpoint</th>
                                <th>Method</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            {[
                                ['/api/v1/datasets/upload', 'POST', 'Upload CSV dataset'],
                                ['/api/v1/models/train', 'POST', 'Start SISA training'],
                                ['/api/v1/data/unlearn', 'POST', 'Unlearn data points'],
                                ['/api/v1/verify/verify', 'POST', 'Run MIA verification'],
                                ['/api/v1/certificates/{id}', 'GET', 'Download certificate'],
                                ['/health', 'GET', 'Health check'],
                                ['/docs', 'GET', 'OpenAPI documentation'],
                            ].map(([endpoint, method, desc]) => (
                                <tr key={endpoint}>
                                    <td style={{ fontFamily: 'monospace', fontSize: '13px' }}>{endpoint}</td>
                                    <td><Badge status={method} variant="neutral" /></td>
                                    <td>{desc}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    );
}
