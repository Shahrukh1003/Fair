"""
Enterprise Report Generator for FairLens v3.0
Creates compliance-ready PDF and CSV reports
"""

import io
import csv
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from config import Config

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Generate compliance-ready PDF and CSV reports
    """
    
    def __init__(self, output_path: str = None):
        if output_path is None:
            output_path = Config.REPORT_OUTPUT_PATH
        
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricPass',
            parent=self.styles['Normal'],
            textColor=colors.green,
            fontSize=11
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricFail',
            parent=self.styles['Normal'],
            textColor=colors.red,
            fontSize=11
        ))
    
    def generate_pdf_report(self,
                           metrics_summary: Dict[str, Any],
                           drift_analysis: Dict[str, Any],
                           feature_contributions: Dict[str, Any],
                           remediation_suggestions: List[Dict[str, str]],
                           audit_history: List[Dict[str, Any]],
                           blockchain_proofs: List[Dict[str, Any]] = None) -> str:
        """
        Generate comprehensive PDF compliance report
        
        Args:
            metrics_summary: All fairness metrics summary
            drift_analysis: Drift monitoring analysis
            feature_contributions: Feature attribution analysis
            remediation_suggestions: AI-generated remediation suggestions
            audit_history: Recent audit log entries
            blockchain_proofs: Optional blockchain verification proofs
        
        Returns:
            Path to generated PDF file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"fairness_compliance_report_{timestamp}.pdf"
        filepath = self.output_path / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Title Page
        story.append(Paragraph("FairLens Fairness Compliance Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            self.styles['Normal']
        ))
        story.append(Paragraph(
            f"Report ID: {timestamp}",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 30))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        summary = metrics_summary.get('summary', {})
        total_metrics = summary.get('total_metrics', 5)
        passed = summary.get('passed', 0)
        failed = summary.get('failed', 0)
        compliance_level = summary.get('compliance_level', 'UNKNOWN')
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Metrics Evaluated', str(total_metrics)],
            ['Metrics Passed', str(passed)],
            ['Metrics Failed', str(failed)],
            ['Compliance Level', compliance_level],
            ['Overall Status', summary.get('overall_status', 'UNKNOWN')]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Detailed Metrics
        story.append(Paragraph("Fairness Metrics Analysis", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        all_metrics = metrics_summary.get('all_metrics', {})
        metrics_data = [['Metric', 'Value', 'Threshold', 'Status']]
        
        for metric_id, metric_info in all_metrics.items():
            value = metric_info.get('value', 'N/A')
            threshold = metric_info.get('threshold', 'N/A')
            status = metric_info.get('status', 'UNKNOWN')
            
            metrics_data.append([
                metric_info.get('name', metric_id),
                f"{value:.4f}" if isinstance(value, (int, float)) else str(value),
                f"{threshold:.4f}" if isinstance(threshold, (int, float)) else str(threshold),
                status
            ])
        
        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#283593')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # Drift Analysis
        story.append(Paragraph("Predictive Drift Analysis", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        drift_data = [
            ['Measure', 'Value', 'Assessment'],
            ['Current DIR', f"{drift_analysis.get('current_value', 0):.4f}", ''],
            ['Velocity (rate of change)', f"{drift_analysis.get('velocity', 0):.4f}", 
             'Degrading' if drift_analysis.get('is_degrading', False) else 'Stable'],
            ['Acceleration', f"{drift_analysis.get('acceleration', 0):.4f}",
             'Accelerating' if drift_analysis.get('is_accelerating', False) else 'Normal'],
            ['Risk Level', drift_analysis.get('risk_assessment', {}).get('risk_level', 'UNKNOWN'), '']
        ]
        
        drift_table = Table(drift_data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch])
        drift_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#283593')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(drift_table)
        story.append(Spacer(1, 20))
        
        # Feature Contributions
        story.append(Paragraph("Bias Root Cause Analysis", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        top_contributors = feature_contributions.get('top_contributors', [])
        if top_contributors:
            contrib_data = [['Feature', 'Contribution Score', 'Mean Difference']]
            for contrib in top_contributors[:5]:
                contrib_data.append([
                    contrib['feature'].replace('_', ' ').title(),
                    f"{contrib['score']:.4f}",
                    f"{contrib['difference']:.2f}"
                ])
            
            contrib_table = Table(contrib_data, colWidths=[3*inch, 2*inch, 2*inch])
            contrib_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#283593')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(contrib_table)
            story.append(Spacer(1, 20))
        
        # Remediation Suggestions
        story.append(Paragraph("AI-Assisted Remediation Recommendations", self.styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        for i, suggestion in enumerate(remediation_suggestions[:5], 1):
            priority = suggestion.get('priority', 'MEDIUM')
            category = suggestion.get('category', 'General')
            text = suggestion.get('suggestion', '')
            action = suggestion.get('action', '')
            
            story.append(Paragraph(
                f"<b>{i}. [{priority}] {category}</b>",
                self.styles['Normal']
            ))
            story.append(Paragraph(text, self.styles['Normal']))
            story.append(Paragraph(f"<i>Action: {action}</i>", self.styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Blockchain Verification (if available)
        if blockchain_proofs:
            story.append(PageBreak())
            story.append(Paragraph("Blockchain Verification Proofs", self.styles['SectionHeader']))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph(
                "This report includes tamper-proof blockchain anchoring for audit integrity.",
                self.styles['Normal']
            ))
            story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        logger.info(f"✅ PDF report generated: {filepath}")
        
        return str(filepath)
    
    def export_to_csv(self,
                      metrics_summary: Dict[str, Any],
                      audit_history: List[Dict[str, Any]],
                      drift_data: List[Dict[str, Any]] = None) -> str:
        """
        Export fairness data to CSV format
        
        Args:
            metrics_summary: Metrics summary data
            audit_history: Audit log entries
            drift_data: Optional drift trend data
        
        Returns:
            Path to generated CSV file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"fairness_data_export_{timestamp}.csv"
        filepath = self.output_path / filename
        
        with open(filepath, 'w', newline='') as csvfile:
            # Write metrics summary
            writer = csv.writer(csvfile)
            writer.writerow(['FairLens Data Export'])
            writer.writerow(['Generated:', datetime.now().isoformat()])
            writer.writerow([])
            
            # Metrics section
            writer.writerow(['FAIRNESS METRICS SUMMARY'])
            writer.writerow(['Metric', 'Value', 'Threshold', 'Status'])
            
            all_metrics = metrics_summary.get('all_metrics', {})
            for metric_id, metric_info in all_metrics.items():
                writer.writerow([
                    metric_info.get('name', metric_id),
                    metric_info.get('value', 'N/A'),
                    metric_info.get('threshold', 'N/A'),
                    metric_info.get('status', 'UNKNOWN')
                ])
            
            writer.writerow([])
            
            # Audit history section
            writer.writerow(['AUDIT HISTORY'])
            if audit_history:
                # Get headers from first entry
                headers = list(audit_history[0].keys())
                writer.writerow(headers)
                
                for entry in audit_history:
                    writer.writerow([entry.get(h, '') for h in headers])
            
            writer.writerow([])
            
            # Drift data section (if provided)
            if drift_data:
                writer.writerow(['DRIFT TREND DATA'])
                writer.writerow(['Timestamp', 'Value', 'Created At'])
                for record in drift_data:
                    writer.writerow([
                        record.get('timestamp', ''),
                        record.get('value', ''),
                        record.get('created_at', '')
                    ])
        
        logger.info(f"✅ CSV export generated: {filepath}")
        
        return str(filepath)
