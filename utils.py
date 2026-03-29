# ===================== utils.py =====================
import smtplib
from email.message import EmailMessage
from datetime import datetime

# ===================== EMAIL CONFIG =====================
EMAIL_SENDER = "s24_pawde_vaishnavi@mgmcen.ac.in"
EMAIL_PASSWORD = "myfy xufw nsaw awew"   # Gmail App Password
ALERT_THRESHOLD = 6  # % change threshold for sending alerts

# ===================== SEND EMAIL ALERT =====================
def send_email_alert(subject, body, recipient_email):
    """
    Sends an email alert using Gmail SMTP.
    """
    try:
        msg = EmailMessage()
        msg['From'] = EMAIL_SENDER
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.set_content(body)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"✅ Alert sent successfully to {recipient_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


# ===================== CHECK CRYPTO ALERTS =====================
def check_crypto_alerts(latest_changes, user_email):
    """
    Checks % changes and sends alert if any coin moves beyond threshold.
    latest_changes: dict like {"Bitcoin": 7.5, "Ethereum": -4.2, ...}
    """
    alerts_sent = 0
    for coin, change in latest_changes.items():
        if abs(change) >= ALERT_THRESHOLD:
            subject = f"🚨 Crypto Alert: Significant Movement in {coin}"
            body = f"""Hello,

{coin} has shown a significant price movement of {change:.2f}% today ({datetime.now().strftime('%Y-%m-%d')}).

This exceeds our alert threshold of {ALERT_THRESHOLD}%.

Recommendation: Please review your portfolio and consider rebalancing if needed.

Best regards,
CryptoMilestone Team
"""
            if send_email_alert(subject, body, user_email):
                alerts_sent += 1

    if alerts_sent > 0:
        print(f"📧 Total alerts sent: {alerts_sent}")
    else:
        print("ℹ️ No alerts triggered today.")


# ===================== RISK LEVEL HELPER =====================
def get_risk_level(percent):
    """
    Returns risk level based on allocation percentage.
    """
    if percent >= 50:
        return "Low Risk"
    elif percent >= 30:
        return "Medium Risk"
    else:
        return "High Risk"