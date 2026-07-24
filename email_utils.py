import smtplib
import streamlit as st

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(
    to_email,
    subject,
    body,
):
    smtp_server = st.secrets["email"]["smtp_server"]
    smtp_port = int(st.secrets["email"]["smtp_port"])
    sender_email = st.secrets["email"]["address"]
    sender_password = st.secrets["email"]["password"]

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


def send_request_notification(
    request_id,
    requester_name,
    requester_email,
    molecule_name,
    calculation_type,
    scientific_question,
    admin_email,
):
    ticket_number = f"DFT-{request_id:04d}"

    subject = f"New DFT Request: {ticket_number}"

    body = f"""
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
        subject,
        body,
    )
