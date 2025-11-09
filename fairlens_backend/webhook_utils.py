"""
Webhook & Alert Notification Module for BiasCheck v3.0

Sends real-time alerts when fairness violations are detected.
Supports Slack webhooks, email notifications, and custom webhooks.
"""

import os
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Webhook Configuration
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')
EMAIL_WEBHOOK_URL = os.getenv('EMAIL_WEBHOOK_URL', '')
CUSTOM_WEBHOOK_URL = os.getenv('CUSTOM_WEBHOOK_URL', '')
WEBHOOK_TIMEOUT = int(os.getenv('WEBHOOK_TIMEOUT', 10))
WEBHOOK_ENABLED = os.getenv('WEBHOOK_ENABLED', 'true').lower() == 'true'


def send_slack_alert(message: str, metrics: Dict[str, Any], severity: str = 'warning') -> bool:
    """
    Send alert to Slack webhook
    
    Args:
        message: Main alert message
        metrics: Dictionary of fairness metrics
        severity: Alert severity (info, warning, critical)
    
    Returns:
        True if successful, False otherwise
    """
    if not SLACK_WEBHOOK_URL or not WEBHOOK_ENABLED:
        logger.debug("Slack webhook not configured or disabled")
        return False
    
    # Color based on severity
    color_map = {
        'info': '#36a64f',      # Green
        'warning': '#ff9900',   # Orange
        'critical': '#ff0000'   # Red
    }
    
    color = color_map.get(severity, '#ff9900')
    
    # Build Slack message fields
    fields = []
    for name, value in metrics.items():
        fields.append({
            'title': 'Metric',
            'value': name,
            'short': True
        })
        fields.append({
            'title': 'Value',
            'value': f"{value:.3f}" if isinstance(value, float) else str(value),
            'short': True
        })
    
    payload = {
        'attachments': [{
            'color': color,
            'title': '⚠️ BiasCheck Fairness Alert',
            'text': message,
            'fields': fields,
            'footer': 'BiasCheck v3.0 - Predictive Fairness Governance',
            'ts': int(datetime.now().timestamp())
        }]
    }
    
    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=payload,
            timeout=WEBHOOK_TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        logger.info(f"Slack alert sent successfully (severity: {severity})")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Slack alert: {e}")
        return False


def send_email_alert(
    subject: str,
    message: str,
    metrics: Dict[str, Any],
    severity: str = 'warning'
) -> bool:
    """
    Send alert via email webhook (e.g., SendGrid, Mailgun)
    
    Args:
        subject: Email subject line
        message: Email body message
        metrics: Dictionary of fairness metrics
        severity: Alert severity
    
    Returns:
        True if successful, False otherwise
    """
    if not EMAIL_WEBHOOK_URL or not WEBHOOK_ENABLED:
        logger.debug("Email webhook not configured or disabled")
        return False
    
    # Build metrics table rows
    metrics_rows = []
    for k, v in metrics.items():
        value_str = f"{v:.3f}" if isinstance(v, float) else str(v)
        metrics_rows.append(f'<tr><td>{k}</td><td>{value_str}</td></tr>')
    metrics_table = ''.join(metrics_rows)
    
    # Build email payload (format depends on your email service)
    color = '#ff0000' if severity == 'critical' else '#ff9900'
    payload = {
        'subject': subject,
        'html': f"""
        <html>
        <body>
            <h2 style="color: {color};">
                ⚠️ BiasCheck Fairness Alert
            </h2>
            <p><strong>Severity:</strong> {severity.upper()}</p>
            <p>{message}</p>
            <h3>Metrics Snapshot:</h3>
            <table border="1" cellpadding="8" style="border-collapse: collapse;">
                <tr><th>Metric</th><th>Value</th></tr>
                {metrics_table}
            </table>
            <hr>
            <p><em>BiasCheck v3.0 - Predictive Fairness Governance</em></p>
            <p><small>Timestamp: {datetime.now().isoformat()}</small></p>
        </body>
        </html>
        """,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            EMAIL_WEBHOOK_URL,
            json=payload,
            timeout=WEBHOOK_TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        logger.info(f"Email alert sent successfully (severity: {severity})")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send email alert: {e}")
        return False


def send_custom_webhook(
    event_type: str,
    data: Dict[str, Any],
    severity: str = 'warning'
) -> bool:
    """
    Send alert to custom webhook endpoint
    
    Args:
        event_type: Type of event (e.g., 'bias_detected', 'drift_alert')
        data: Event data payload
        severity: Alert severity
    
    Returns:
        True if successful, False otherwise
    """
    if not CUSTOM_WEBHOOK_URL or not WEBHOOK_ENABLED:
        logger.debug("Custom webhook not configured or disabled")
        return False
    
    payload = {
        'event_type': event_type,
        'severity': severity,
        'timestamp': datetime.now().isoformat(),
        'source': 'fairlens_v3.0',
        'data': data
    }
    
    try:
        response = requests.post(
            CUSTOM_WEBHOOK_URL,
            json=payload,
            timeout=WEBHOOK_TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        logger.info(f"Custom webhook sent successfully (event: {event_type}, severity: {severity})")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send custom webhook: {e}")
        return False


def send_fairness_alert(
    alert_type: str,
    metrics: Dict[str, Any],
    threshold: float,
    actual_value: float,
    record_id: Optional[str] = None
) -> Dict[str, bool]:
    """
    Send fairness violation alert through all configured channels
    
    Args:
        alert_type: Type of fairness violation (e.g., 'DIR_VIOLATION')
        metrics: All fairness metrics
        threshold: Expected threshold value
        actual_value: Actual measured value
        record_id: Optional compliance record ID
    
    Returns:
        Dictionary showing success status for each channel
    """
    # Determine severity
    if actual_value < threshold * 0.7:
        severity = 'critical'
    elif actual_value < threshold * 0.85:
        severity = 'warning'
    else:
        severity = 'info'
    
    # Build message
    message = f"""
🚨 Fairness Alert: {alert_type}

**Threshold:** {threshold:.3f}
**Actual Value:** {actual_value:.3f}
**Deviation:** {((actual_value - threshold) / threshold * 100):.1f}%

A fairness metric has fallen below the acceptable threshold, indicating potential bias in model predictions.
"""
    
    if record_id:
        message += f"\n**Record ID:** {record_id}"
    
    # Send to all channels
    results = {
        'slack': send_slack_alert(message, metrics, severity),
        'email': send_email_alert(
            subject=f'🚨 BiasCheck Alert: {alert_type}',
            message=message,
            metrics=metrics,
            severity=severity
        ),
        'custom': send_custom_webhook(
            event_type=alert_type.lower(),
            data={
                'metrics': metrics,
                'threshold': threshold,
                'actual_value': actual_value,
                'record_id': record_id,
                'deviation_percent': ((actual_value - threshold) / threshold * 100)
            },
            severity=severity
        )
    }
    
    # Log results
    sent_count = sum(1 for success in results.values() if success)
    if sent_count > 0:
        logger.info(f"Fairness alert sent to {sent_count} channel(s): {alert_type}")
    else:
        logger.warning(f"Failed to send fairness alert to any channel: {alert_type}")
    
    return results


def test_webhook_configuration() -> Dict[str, Any]:
    """
    Test webhook configuration by sending test messages
    
    Returns:
        Dictionary with test results for each channel
    """
    test_metrics = {
        'DIR': 0.75,
        'SPD': 0.08,
        'EOD': 0.06,
        'AOD': 0.05,
        'THEIL': 0.12
    }
    
    results = {
        'slack': {
            'configured': bool(SLACK_WEBHOOK_URL),
            'enabled': WEBHOOK_ENABLED,
            'test_sent': False,
            'test_passed': False
        },
        'email': {
            'configured': bool(EMAIL_WEBHOOK_URL),
            'enabled': WEBHOOK_ENABLED,
            'test_sent': False,
            'test_passed': False
        },
        'custom': {
            'configured': bool(CUSTOM_WEBHOOK_URL),
            'enabled': WEBHOOK_ENABLED,
            'test_sent': False,
            'test_passed': False
        }
    }
    
    if WEBHOOK_ENABLED:
        if SLACK_WEBHOOK_URL:
            results['slack']['test_sent'] = True
            results['slack']['test_passed'] = send_slack_alert(
                'This is a test alert from BiasCheck v3.0',
                test_metrics,
                'info'
            )
        
        if EMAIL_WEBHOOK_URL:
            results['email']['test_sent'] = True
            results['email']['test_passed'] = send_email_alert(
                'BiasCheck Test Alert',
                'This is a test alert from BiasCheck v3.0',
                test_metrics,
                'info'
            )
        
        if CUSTOM_WEBHOOK_URL:
            results['custom']['test_sent'] = True
            results['custom']['test_passed'] = send_custom_webhook(
                'test_alert',
                {'message': 'Test from BiasCheck v3.0', 'metrics': test_metrics},
                'info'
            )
    
    return results
