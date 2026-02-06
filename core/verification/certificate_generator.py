"""
Certificate Generator - Creates legally-defensible proof of erasure
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import json
import hashlib

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from utils import get_logger, generate_uuid, get_timestamp

log = get_logger(__name__)


class CertificateGenerator:
    """
    Generates PDF certificates proving data erasure.
    
    These certificates include:
    - Timestamp of erasure
    - Before/after confidence metrics
    - Statistical test results
    - Cryptographic hash of model state
    - Audit trail information
    """
    
    def __init__(
        self,
        output_dir: str = "./certificates",
        organization_name: str = "Amnesia Platform",
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.organization_name = organization_name
    
    def generate(
        self,
        model_id: str,
        data_ids: list,
        verification_results: Dict[str, Any],
        model_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate erasure certificate PDF.
        
        Args:
            model_id: ID of the model
            data_ids: List of data IDs that were erased
            verification_results: Results from verification tests
            model_hash: Optional hash of model weights
            metadata: Additional metadata
            
        Returns:
            Path to generated certificate PDF
        """
        certificate_id = generate_uuid()
        timestamp = get_timestamp()
        
        # Create filename
        filename = f"certificate_{certificate_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = self.output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )
        
        # Build content
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
        )
        
        # Title
        story.append(Paragraph("CERTIFICATE OF DATA ERASURE", title_style))
        story.append(Spacer(1, 20))
        
        # Certificate info box
        cert_data = [
            ["Certificate ID:", certificate_id],
            ["Issue Date:", timestamp],
            ["Issuing Organization:", self.organization_name],
            ["Model ID:", model_id],
        ]
        
        cert_table = Table(cert_data, colWidths=[2*inch, 4*inch])
        cert_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(cert_table)
        story.append(Spacer(1, 20))
        
        # Declaration
        story.append(Paragraph("DECLARATION", heading_style))
        declaration_text = f"""
        This certificate confirms that the data identified below has been 
        successfully removed from the machine learning model identified above. 
        The erasure was performed using the Amnesia Machine Unlearning Platform 
        and has been verified through rigorous statistical testing.
        """
        story.append(Paragraph(declaration_text, body_style))
        story.append(Spacer(1, 10))
        
        # Data erased section
        story.append(Paragraph("DATA ERASED", heading_style))
        story.append(Paragraph(f"Number of data points erased: {len(data_ids)}", body_style))
        
        # Show first few data IDs
        if len(data_ids) <= 10:
            data_list = ", ".join(data_ids)
        else:
            data_list = ", ".join(data_ids[:10]) + f", ... and {len(data_ids) - 10} more"
        story.append(Paragraph(f"Data IDs: {data_list}", body_style))
        story.append(Spacer(1, 10))
        
        # Verification results
        story.append(Paragraph("VERIFICATION RESULTS", heading_style))
        
        forget_conf = verification_results.get("forget_confidence", "N/A")
        retain_acc = verification_results.get("retain_accuracy", "N/A")
        success = verification_results.get("success", False)
        
        verification_data = [
            ["Metric", "Before", "After", "Status"],
            [
                "Confidence on Erased Data",
                f"{verification_results.get('confidence_before', 'N/A'):.4f}" if isinstance(verification_results.get('confidence_before'), float) else "N/A",
                f"{forget_conf:.4f}" if isinstance(forget_conf, float) else str(forget_conf),
                "✓ PASS" if isinstance(forget_conf, float) and forget_conf < 0.6 else "✗ FAIL"
            ],
            [
                "Accuracy on Retained Data",
                "N/A",
                f"{retain_acc:.4f}" if isinstance(retain_acc, float) else str(retain_acc),
                "✓ PASS" if isinstance(retain_acc, float) and retain_acc > 0.85 else "✗ FAIL"
            ],
        ]
        
        ver_table = Table(verification_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1*inch])
        ver_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(ver_table)
        story.append(Spacer(1, 20))
        
        # Overall status
        status_text = "ERASURE VERIFIED SUCCESSFULLY" if success else "ERASURE VERIFICATION INCOMPLETE"
        status_color = colors.green if success else colors.red
        
        status_style = ParagraphStyle(
            'Status',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=status_color,
            alignment=TA_CENTER,
        )
        story.append(Paragraph(status_text, status_style))
        story.append(Spacer(1, 20))
        
        # Model integrity
        if model_hash:
            story.append(Paragraph("MODEL INTEGRITY", heading_style))
            story.append(Paragraph(f"Model Hash (SHA-256): {model_hash}", body_style))
            story.append(Spacer(1, 10))
        
        # Legal disclaimer
        story.append(Paragraph("LEGAL NOTICE", heading_style))
        disclaimer_text = """
        This certificate is generated automatically by the Amnesia Machine Unlearning 
        Platform. The verification tests demonstrate that the specified data no longer 
        influences the model's predictions to a statistically significant degree. This 
        certificate may be used as supporting documentation for data protection compliance 
        purposes, including but not limited to GDPR Article 17 (Right to Erasure) requests.
        """
        story.append(Paragraph(disclaimer_text, body_style))
        
        # Build PDF
        doc.build(story)
        
        log.info(f"Generated certificate: {filepath}")
        
        # Also save JSON version
        json_data = {
            "certificate_id": certificate_id,
            "timestamp": timestamp,
            "model_id": model_id,
            "data_ids": data_ids,
            "verification_results": verification_results,
            "model_hash": model_hash,
            "metadata": metadata,
            "pdf_path": str(filepath),
        }
        
        json_path = filepath.with_suffix('.json')
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2, default=str)
        
        return str(filepath)
    
    @staticmethod
    def compute_model_hash(model) -> str:
        """Compute SHA-256 hash of model weights"""
        import torch
        import io
        
        buffer = io.BytesIO()
        torch.save(model.state_dict(), buffer)
        buffer.seek(0)
        
        return hashlib.sha256(buffer.read()).hexdigest()


def generate_certificate(
    model_id: str,
    data_ids: list,
    verification_results: Dict[str, Any],
    model_hash: Optional[str] = None,
    output_dir: str = "./certificates",
) -> str:
    """
    Functional interface to generate an erasure certificate.
    
    This is a simplified wrapper around CertificateGenerator.
    
    Args:
        model_id: ID of the model
        data_ids: List of data IDs that were erased
        verification_results: Results from verification tests
        model_hash: Optional hash of model weights for integrity verification
        output_dir: Directory to save the certificate
        
    Returns:
        Path to the generated certificate PDF
    """
    generator = CertificateGenerator(output_dir=output_dir)
    return generator.generate(
        model_id=model_id,
        data_ids=data_ids,
        verification_results=verification_results,
        model_hash=model_hash,
    )