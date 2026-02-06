'use client';

import { useState, useEffect } from 'react';
import { Card, Button, Badge, UploadZone, DataTable, Alert } from '@/components/ui';
import api from '@/lib/api';

export default function DatasetsPage() {
    const [datasets, setDatasets] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState(null);
    const [preview, setPreview] = useState(null);

    useEffect(() => {
        fetchDatasets();
    }, []);

    const fetchDatasets = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v1/datasets/list');
            if (response.ok) {
                const data = await response.json();
                setDatasets(data.datasets || []);
            }
        } catch (err) {
            console.log('Could not fetch datasets');
        }
    };

    const handleUpload = async (file) => {
        setUploading(true);
        setMessage(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/api/v1/datasets/upload', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                setMessage({ type: 'success', text: `Dataset "${data.dataset.name}" uploaded successfully!` });
                fetchDatasets();
            } else {
                setMessage({ type: 'danger', text: data.detail || 'Upload failed' });
            }
        } catch (err) {
            setMessage({ type: 'danger', text: 'Failed to connect to API' });
        }

        setUploading(false);
    };

    const handlePreview = async (filename) => {
        try {
            const response = await fetch(`http://localhost:8000/api/v1/datasets/${filename}/preview`);
            if (response.ok) {
                const data = await response.json();
                setPreview({ filename, ...data });
            }
        } catch (err) {
            console.error('Preview failed');
        }
    };

    const handleDelete = async (filename) => {
        try {
            const response = await fetch(`http://localhost:8000/api/v1/datasets/${filename}`, {
                method: 'DELETE',
            });
            if (response.ok) {
                setMessage({ type: 'success', text: 'Dataset deleted' });
                fetchDatasets();
                if (preview?.filename === filename) setPreview(null);
            }
        } catch (err) {
            setMessage({ type: 'danger', text: 'Delete failed' });
        }
    };

    const formatBytes = (bytes) => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1>Datasets</h1>
                <p>Upload and manage your training data</p>
            </div>

            {message && (
                <Alert type={message.type}>{message.text}</Alert>
            )}

            <div className="two-columns">
                <div>
                    <Card title="📤 Upload Dataset">
                        <UploadZone
                            onFileSelect={handleUpload}
                            accept=".csv"
                            hint="Supported format: CSV with headers. Include a 'label' column for classification."
                        />
                        {uploading && (
                            <div style={{ textAlign: 'center', marginTop: '16px', color: 'var(--text-secondary)' }}>
                                Uploading...
                            </div>
                        )}
                    </Card>

                    <Card title="📋 Your Datasets" className="fade-in" style={{ marginTop: '24px' }}>
                        {datasets.length === 0 ? (
                            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
                                No datasets uploaded yet
                            </div>
                        ) : (
                            <div>
                                {datasets.map((ds) => (
                                    <div
                                        key={ds.filename}
                                        style={{
                                            padding: '12px',
                                            borderBottom: '1px solid var(--border-default)',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'space-between',
                                        }}
                                    >
                                        <div>
                                            <div style={{ fontWeight: 500, color: 'var(--text-primary)' }}>
                                                {ds.name}
                                            </div>
                                            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                                                {ds.rows.toLocaleString()} rows • {ds.columns} columns • {formatBytes(ds.size_bytes)}
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', gap: '8px' }}>
                                            <Button variant="secondary" onClick={() => handlePreview(ds.filename)}>
                                                Preview
                                            </Button>
                                            <Button variant="danger" onClick={() => handleDelete(ds.filename)}>
                                                Delete
                                            </Button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </Card>
                </div>

                <div>
                    {preview ? (
                        <Card title={`Preview: ${preview.filename}`}>
                            <div style={{ marginBottom: '16px', color: 'var(--text-secondary)', fontSize: '14px' }}>
                                Showing first {preview.data.length} of {preview.total_rows.toLocaleString()} rows
                            </div>
                            <div style={{ overflowX: 'auto' }}>
                                <table>
                                    <thead>
                                        <tr>
                                            {preview.columns.map((col) => (
                                                <th key={col}>{col}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {preview.data.map((row, idx) => (
                                            <tr key={idx}>
                                                {preview.columns.map((col) => (
                                                    <td key={col}>{String(row[col]).substring(0, 50)}</td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </Card>
                    ) : (
                        <Card title="ℹ️ How It Works">
                            <div style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: 1.7 }}>
                                <p style={{ marginBottom: '16px' }}>
                                    <strong>1. Upload your data</strong><br />
                                    CSV file with features and a target/label column
                                </p>
                                <p style={{ marginBottom: '16px' }}>
                                    <strong>2. Train your model</strong><br />
                                    Data is sharded using SISA architecture for efficient unlearning
                                </p>
                                <p style={{ marginBottom: '16px' }}>
                                    <strong>3. Request deletion</strong><br />
                                    Specify row indices to remove from the model
                                </p>
                                <p>
                                    <strong>4. Get certified</strong><br />
                                    Verification generates a legal compliance certificate
                                </p>
                            </div>
                        </Card>
                    )}

                    <Card title="📊 Sample Datasets" style={{ marginTop: '24px' }}>
                        <div style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
                            <p style={{ marginBottom: '12px' }}>Don't have data? Try these built-in datasets:</p>
                            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                                <Badge status="MNIST" variant="neutral" />
                                <Badge status="CIFAR-10" variant="neutral" />
                                <Badge status="CIFAR-100" variant="neutral" />
                            </div>
                            <p style={{ marginTop: '12px', fontSize: '12px', color: 'var(--text-muted)' }}>
                                Available in the Training page
                            </p>
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
}
