'use client';

import { useState } from 'react';
import { Card, Button, FormGroup, Slider, ProgressBar, Alert, Badge } from '@/components/ui';
import api from '@/lib/api';

export default function TrainingPage() {
    const [config, setConfig] = useState({
        datasetName: 'mnist',
        modelType: 'SimpleMLP',
        numShards: 4,
        epochs: 50,
    });
    const [isTraining, setIsTraining] = useState(false);
    const [progress, setProgress] = useState(0);
    const [message, setMessage] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsTraining(true);
        setProgress(0);
        setMessage(null);

        try {
            const response = await api.startTraining(config);

            if (response.success) {
                // Simulate progress
                const interval = setInterval(() => {
                    setProgress(prev => {
                        if (prev >= 100) {
                            clearInterval(interval);
                            setIsTraining(false);
                            setMessage({ type: 'success', text: 'Training completed! Model ready for unlearning.' });
                            return 100;
                        }
                        return prev + 2;
                    });
                }, 100);
            } else {
                setMessage({ type: 'danger', text: response.error || 'Training failed' });
                setIsTraining(false);
            }
        } catch (err) {
            setMessage({ type: 'danger', text: 'Failed to connect to API' });
            setIsTraining(false);
        }
    };

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1>Training</h1>
                <p>Train models using SISA (Sharded, Isolated, Sliced, Aggregated) architecture</p>
            </div>

            {message && <Alert type={message.type}>{message.text}</Alert>}

            <div className="two-columns">
                <Card title="⚙️ Configuration">
                    <form onSubmit={handleSubmit}>
                        <FormGroup label="Dataset">
                            <select
                                className="form-select"
                                value={config.datasetName}
                                onChange={(e) => setConfig({ ...config, datasetName: e.target.value })}
                            >
                                <option value="mnist">MNIST (Handwritten Digits)</option>
                                <option value="cifar10">CIFAR-10 (Objects)</option>
                                <option value="cifar100">CIFAR-100 (Fine-grained)</option>
                                <option value="custom">Custom (from Datasets page)</option>
                            </select>
                        </FormGroup>

                        <FormGroup label="Model">
                            <select
                                className="form-select"
                                value={config.modelType}
                                onChange={(e) => setConfig({ ...config, modelType: e.target.value })}
                            >
                                <option value="SimpleMLP">SimpleMLP (Fast, CPU)</option>
                                <option value="ResNet18">ResNet18 (Accurate)</option>
                            </select>
                        </FormGroup>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                            <FormGroup label={`Shards: ${config.numShards}`} hint="More shards = faster unlearning">
                                <Slider
                                    value={config.numShards}
                                    onChange={(v) => setConfig({ ...config, numShards: v })}
                                    min={2} max={8}
                                />
                            </FormGroup>

                            <FormGroup label={`Epochs: ${config.epochs}`}>
                                <Slider
                                    value={config.epochs}
                                    onChange={(v) => setConfig({ ...config, epochs: v })}
                                    min={10} max={100} step={10}
                                />
                            </FormGroup>
                        </div>

                        <Button type="submit" variant="primary" fullWidth disabled={isTraining}>
                            {isTraining ? `Training... ${progress}%` : 'Start Training'}
                        </Button>
                    </form>
                </Card>

                <div>
                    <Card title="📊 Progress">
                        {isTraining ? (
                            <>
                                <ProgressBar progress={progress} />
                                <div style={{ textAlign: 'center', marginTop: '16px', color: 'var(--text-secondary)' }}>
                                    Training shard {Math.ceil((progress / 100) * config.numShards)} of {config.numShards}
                                </div>
                                <div style={{ textAlign: 'center', marginTop: '8px' }}>
                                    <Badge status={config.datasetName.toUpperCase()} variant="neutral" />
                                </div>
                            </>
                        ) : progress === 100 ? (
                            <div style={{ textAlign: 'center', padding: '24px' }}>
                                <div style={{ fontSize: '32px', marginBottom: '12px' }}>✅</div>
                                <div style={{ color: 'var(--accent-success)', fontWeight: 500 }}>Training Complete</div>
                                <a href="/unlearning">
                                    <Button variant="secondary" style={{ marginTop: '16px' }}>
                                        Proceed to Unlearning →
                                    </Button>
                                </a>
                            </div>
                        ) : (
                            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                                Configure settings and click Start
                            </div>
                        )}
                    </Card>

                    <Card title="ℹ️ SISA Architecture" style={{ marginTop: '24px' }}>
                        <div style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: 1.7 }}>
                            <p>
                                <strong>Why sharding?</strong><br />
                                Data is split into isolated shards. Each shard trains its own model.
                                When deletion required, only affected shard retrains.
                            </p>
                            <div style={{
                                marginTop: '16px',
                                padding: '12px',
                                background: 'var(--bg-tertiary)',
                                borderRadius: 'var(--radius-md)',
                                fontFamily: 'monospace',
                                fontSize: '12px',
                            }}>
                                4 shards = 75% faster unlearning<br />
                                8 shards = 87.5% faster unlearning
                            </div>
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
}
