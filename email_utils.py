import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_email, subject, body):
    """
    Send an email using SMTP credentials stored
    as environment variables.
    """

    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")

    if not sender_email or not sender_password:
        raise RuntimeError(
            "SMTP_EMAIL and SMTP_PASSWORD environment variables must be set."
        )

    message = MIMEMultipart()

    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(
        MIMEText(body, "plain")
    )

    with smtplib.SMTP(
        smtp_server,
        smtp_port,
    ) as server:

        server.starttls()

        server.login(
            sender_email,
            sender_password,
        )

        server.send_message(message)


def send_request_notifications(
    request_id,
    requester_name,
    requester_email,
    molecule_name,
    calculation_type,
    scientific_question,
    admin_email,
):
    """
    Send confirmation to requester and notification
    to the DFT administrator.
    """

    ticket_number = f"DFT-{request_id:04d}"

    # --------------------------
    # Email to requester
    # --------------------------

    if requester_email:

        requester_subject = (
            f"{ticket_number} — DFT Request Received"
        )

        requester_body = f"""
Hi {requester_name},

Your DFT calculation request has been received successfully.

Ticket number: {ticket_number}

Molecule / system:
{molecule_name}

Requested calculation:
{calculation_type}

Scientific question:
{scientific_question}

Your request will be reviewed and the appropriate computational approach will be selected based on the chemical context of the problem.

Please reference {ticket_number} if you have any questions about this calculation.

Best,
MCK Lab DFT Portal
"""

        send_email(
            requester_email,
            requester_subject,
            requester_body,
        )

    # --------------------------
    # Email to administrator
    # --------------------------

    admin_subject = (
        f"New DFT Request: {ticket_number}"
    )

    admin_body = f"""
A new DFT calculation request has been submitted.

Ticket:
{ticket_number}

Submitted by:
{requester_name}

Email:
{requester_email or "Not provided"}

Molecule / system:
{molecule_name}

Calculation:
{calculation_type}

Scientific question:
{scientific_question}

Open the DFT Request Portal to review the request.
"""

    send_email(
        admin_email,
        admin_subject,
        admin_body,
    )
