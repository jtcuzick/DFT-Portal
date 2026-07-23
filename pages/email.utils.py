import smtplib
import streamlit as st

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(
    to_email,
    subject,
    body,
):
    """
    Send an email using credentials stored
    in Streamlit secrets.
    """

    smtp_server = st.secrets["email"]["smtp_server"]
    smtp_port = int(st.secrets["email"]["smtp_port"])
    sender_email = st.secrets["email"]["address"]
    sender_password = st.secrets["email"]["password"]

    message = MIMEMultipart()

    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(
        MIMEText(
            body,
            "plain",
        )
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
    Send:
    1. A confirmation email to the requester.
    2. A notification email to the DFT administrator.
    """

    ticket_number = f"DFT-{request_id:04d}"

    # ======================================================
    # REQUESTER CONFIRMATION
    # ======================================================

    requester_subject = (
        f"{ticket_number} — DFT Request Received"
    )

    requester_body = f"""
Hi {requester_name},

Your DFT calculation request has been received successfully.

Ticket number:
{ticket_number}

Molecule / system:
{molecule_name}

Requested calculation:
{calculation_type}

Scientific question:
{scientific_question}

Your request will now be reviewed and the appropriate
computational approach will be selected based on the
chemical context of the problem.

Please reference {ticket_number} if you have any questions
regarding this calculation.

Best,
MCK Lab DFT Portal
"""

    send_email(
        requester_email,
        requester_subject,
        requester_body,
    )

    # ======================================================
    # ADMIN NOTIFICATION
    # ======================================================

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
{requester_email}

Molecule / system:
{molecule_name}

Requested calculation:
{calculation_type}

Scientific question:
{scientific_question}

Open the MCK Lab DFT Portal to review the request.
"""

    send_email(
        admin_email,
        admin_subject,
        admin_body,
    )
