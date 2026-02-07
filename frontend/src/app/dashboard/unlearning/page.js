'use client';

import { useState } from 'react';
import { Card, Button, FormGroup, Slider, ProgressBar, Alert, Badge } from '@/components/ui';
import api from '@/lib/api';

export default function UnlearningPage() {
    const [config, setConfig] = useState({
        dataIndices: '0, 1, 2',
        shardId: 0,
        alpha: 10.0,
        beta: 0.1,
        epochs: 100,
    });
    const [isUnlearning, setIsUnlearning] = useState(false);
    const [progress, setProgress] = useState(0);
    const [message, setMessage] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();

        const indices = config.dataIndices.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n));
        if (indices.length === 0) {
            setMessage({ type: 'danger', text: 'Please enter valid data indices' });
            return;
        }

        setIsUnlearning(true);
        setProgress(0);
        setMessage(null);

        try {
            const response = await api.startUnlearning({ ...config, dataIndices: indices });

            if (response.success) {
                const interval = setInterval(() => {
                    setProgress(prev => {
                        if (prev >= 100) {
                            clearInterval(interval);
                            setIsUnlearning(false);
                            setMessage({ type: 'success', text: `${indices.length} data points unlearned. Proceed to verification.` });
                            return 100;
                        }
                        return prev + 1;
                    });
                }, 30);
            } else {
                setMessage({ type: 'danger', text: response.error || 'Unlearning failed' });
                setIsUnlearning(false);
            }
        } catch (err) {
            setMessage({ type: 'danger', text: 'Failed to connect to API' });
            setIsUnlearning(false);
        }
    };

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1>Unlearning</h1>
                <p>Remove specific data points from trained models using gradient ascent</p>
            </div>

            {message && <Alert type={message.type}>{message.text}</Alert>}

            <div className="two-columns">
                <Card title="🎯 Configuration">
                    <form onSubmit={handleSubmit}>
                        <FormGroup
                            label="Data Indices to Forget"
                            hint="Enter row numbers to remove (comma-separated)"
                        >
                            <textarea
                                className="form-textarea"
                                rows={2}
                                placeholder="e.g., 0, 1, 2, 5, 10"
                                value={config.dataIndices}
                                onChange={(e) => setConfig({ ...config, dataIndices: e.target.value })}
                            />
                        </FormGroup>

                        <FormGroup label="Target Shard">
                            <select
                                className="form-select"
                                value={config.shardId}
                                onChange={(e) => setConfig({ ...config, shardId: parseInt(e.target.value) })}
                            >
                                {[0, 1, 2, 3].map(id => (
                                    <option key={id} value={id}>Shard {id}</option>
                                ))}
                            </select>
                        </FormGroup>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                            <FormGroup label={`α (Forget): ${config.alpha}`} hint="Strength of forgetting">
                                <Slider
                                    value={config.alpha}
                                    onChange={(v) => setConfig({ ...config, alpha: v })}
                                    min={1} max={20} step={0.5}
                                />
                            </FormGroup>

                            <FormGroup label={`β (Retain): ${config.beta}`} hint="Preserve other data">
                                <Slider
                                    value={config.beta}
                                    onChange={(v) => setConfig({ ...config, beta: v })}
                                    min={0.01} max={1} step={0.01}
                                />
                            </FormGroup>
                        </div>

                        <FormGroup label={`Epochs: ${config.epochs}`}>
                            <Slider
                                value={config.epochs}
                                onChange={(v) => setConfig({ ...config, epochs: v })}
                                min={1} max={200} step={1}
                            />
                        </FormGroup>

                        <Button type="submit" variant="danger" fullWidth disabled={isUnlearning}>
                            {isUnlearning ? `Unlearning... ${progress}%` : '🧹 Start Unlearning'}
                        </Button>

                        {progress === 100 && (
                            <a href="/verification">
                                <Button variant="primary" fullWidth style={{ marginTop: '12px' }}>
                                    Proceed to Verification →
                                </Button>
                            </a>
                        )}
                    </form>
                </Card>

                <div>
                    <Card title="📊 Progress">
                        {isUnlearning ? (
                            <>
                                <ProgressBar progress={progress} />
                                <div style={{ textAlign: 'center', marginTop: '16px', color: 'var(--text-secondary)' }}>
                                    Epoch {progress} / {config.epochs}
                                </div>
                            </>
                        ) : progress === 100 ? (
                            <div style={{ textAlign: 'center', padding: '24px' }}>
                                <div style={{ fontSize: '32px', marginBottom: '12px' }}>🧹</div>
                                <div style={{ color: 'var(--accent-success)', fontWeight: 500 }}>Unlearning Complete</div>
                                <div style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '8px' }}>
                                    Now run verification to confirm erasure
                                </div>
                            </div>
                        ) : (
                            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                                Specify data indices to forget
                            </div>
                        )}
                    </Card>

                    <Card title="ℹ️ How Unlearning Works" style={{ marginTop: '24px' }}>
                        <div style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: 1.7 }}>
                            <p><strong style={{ color: 'var(--accent-danger)' }}>α Forget Loss:</strong> Maximize loss on target data (model "forgets" it)</p>
                            <p style={{ marginTop: '8px' }}><strong style={{ color: 'var(--accent-success)' }}>β Retain Loss:</strong> Minimize loss on other data (preserve accuracy)</p>
                            <div style={{
                                marginTop: '16px',
                                padding: '12px',
                                background: 'var(--bg-tertiary)',
                                borderRadius: 'var(--radius-md)',
                                fontFamily: 'monospace',
                                fontSize: '12px',
                            }}>
                                Total Loss = α·forget - β·retain + γ·fisher
                            </div>
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
}
