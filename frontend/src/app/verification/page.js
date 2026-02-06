'use client';

import { useState } from 'react';
import { Card, Button, FormGroup, Slider, Alert, Badge, Gauge } from '@/components/ui';
import api from '@/lib/api';

export default function VerificationPage() {
    const [shardId, setShardId] = useState(0);
    const [threshold, setThreshold] = useState(0.6);
    const [dataIndices, setDataIndices] = useState('0, 1, 2');
    const [isVerifying, setIsVerifying] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleVerify = async (e) => {
        e.preventDefault();
        const indices = dataIndices.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n));

        if (indices.length === 0) {
            setError('Please enter valid data indices');
            return;
        }

        setIsVerifying(true);
        setResult(null);
        setError(null);

        try {
            const response = await api.verifyErasure({
                shard_id: shardId,
                data_indices: indices,
                target_confidence_threshold: threshold,
            });

            if (response.success) {
                setResult({
                    confidence: response.data.confidence_score,
                    isCompliant: response.data.is_erased,
                    certificateUrl: response.data.certificate_url,
                    method: response.data.verification_method,
                });
            } else {
                setError(response.error || 'Verification failed');
            }
        } catch (err) {
            setError('Failed to connect to API');
        }

        setIsVerifying(false);
    };

    const downloadCertificate = (url) => {
        window.open(`http://localhost:8000${url}`, '_blank');
    };

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1>Verification</h1>
                <p>Verify erasure using Membership Inference Attack and generate compliance certificate</p>
            </div>

            {error && <Alert type="danger">{error}</Alert>}

            <div className="two-columns">
                <Card title="🔍 Run Verification">
                    <form onSubmit={handleVerify}>
                        <FormGroup label="Data Indices to Verify" hint="Same indices you used for unlearning">
                            <input
                                type="text"
                                className="form-input"
                                value={dataIndices}
                                onChange={(e) => setDataIndices(e.target.value)}
                                placeholder="e.g., 0, 1, 2"
                            />
                        </FormGroup>

                        <FormGroup label="Target Shard">
                            <select
                                className="form-select"
                                value={shardId}
                                onChange={(e) => setShardId(parseInt(e.target.value))}
                            >
                                {[0, 1, 2, 3].map(id => (
                                    <option key={id} value={id}>Shard {id}</option>
                                ))}
                            </select>
                        </FormGroup>

                        <FormGroup label={`Confidence Threshold: ${(threshold * 100).toFixed(0)}%`} hint="Model confidence below this = data forgotten">
                            <Slider
                                value={threshold}
                                onChange={setThreshold}
                                min={0.3} max={0.9} step={0.05}
                            />
                        </FormGroup>

                        <Button type="submit" variant="primary" fullWidth disabled={isVerifying}>
                            {isVerifying ? 'Verifying...' : '🔍 Verify Erasure'}
                        </Button>
                    </form>
                </Card>

                <div>
                    {result ? (
                        <Card title="📊 Result">
                            <Gauge
                                value={result.confidence}
                                label="Model Confidence"
                                threshold={threshold}
                            />

                            <div style={{
                                marginTop: '24px',
                                padding: '16px',
                                background: result.isCompliant ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                                borderRadius: 'var(--radius-md)',
                                textAlign: 'center',
                            }}>
                                <div style={{
                                    color: result.isCompliant ? 'var(--accent-success)' : 'var(--accent-danger)',
                                    fontWeight: 500,
                                }}>
                                    {result.isCompliant
                                        ? '✅ GDPR Article 17 Compliant'
                                        : '⚠️ Data traces may remain'
                                    }
                                </div>
                                <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginTop: '8px' }}>
                                    Method: {result.method || 'Membership Inference Attack'}
                                </div>
                            </div>

                            {result.isCompliant && result.certificateUrl && (
                                <Button
                                    variant="primary"
                                    fullWidth
                                    onClick={() => downloadCertificate(result.certificateUrl)}
                                    style={{ marginTop: '16px' }}
                                >
                                    📜 Download Certificate (PDF)
                                </Button>
                            )}
                        </Card>
                    ) : (
                        <Card title="ℹ️ About MIA Verification">
                            <div style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: 1.7 }}>
                                <p>
                                    <strong>Membership Inference Attack (MIA)</strong> tests whether the model
                                    "remembers" specific data points.
                                </p>
                                <p style={{ marginTop: '12px' }}>
                                    <strong>Low confidence</strong> = Model doesn't recognize the data = <span style={{ color: 'var(--accent-success)' }}>Successfully forgotten</span>
                                </p>
                                <p style={{ marginTop: '12px' }}>
                                    <strong>High confidence</strong> = Model still recognizes data = <span style={{ color: 'var(--accent-danger)' }}>More unlearning needed</span>
                                </p>
                            </div>
                        </Card>
                    )}

                    <Card title="⚖️ Legal Compliance" style={{ marginTop: '24px' }}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <Badge status="GDPR" variant="success" />
                                <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Article 17 - Right to Erasure</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <Badge status="CCPA" variant="success" />
                                <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>§1798.105 - Right to Delete</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <Badge status="LGPD" variant="success" />
                                <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Article 18 - Data Deletion</span>
                            </div>
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
}
