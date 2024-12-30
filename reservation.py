from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel, EmailStr
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# In-memory storage for tokens (for demonstration purposes)
tokens = {}

# Reservation request model
class ReservationRequest(BaseModel):
    name: str
    email: EmailStr

# Function to send token email
def send_token_email(name, email, token):
    # Gmail SMTP configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "rayenslamaa@gmail.com"  # Replace with your Gmail address
    sender_password = "easb ggda jjkc jkyw"  # Replace with your Gmail app password

    # Email content
    subject = "Museum Reservation Confirmation Token"
    body = f"""Dear {name},

Thank you for starting the reservation process.

Your confirmation token is: {token}

Please enter this token to confirm your reservation.

Best regards,
Museum Team"""

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Connect to Gmail SMTP server and send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        server.send_message(msg)

# Endpoint to reserve a ticket
@app.post("/reserve")
async def reserve_ticket(request: ReservationRequest):
    name = request.name
    email = request.email

    # Generate a random token
    token = str(random.randint(100000, 999999))

    # Save the token for verification
    tokens[email] = token

    # Send token via email
    try:
        send_token_email(name, email, token)
        return {"message": "A confirmation token has been sent to your email."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send token email: {e}")

# Endpoint to confirm reservation using token
class ConfirmationRequest(BaseModel):
    email: EmailStr
    token: str

@app.post("/confirm")
async def confirm_reservation(request: ConfirmationRequest):
    email = request.email
    token = request.token

    if email in tokens and tokens[email] == token:
        del tokens[email]  # Remove the token after successful confirmation
        return {"message": "Reservation confirmed! Thank you."}
    else:
        raise HTTPException(status_code=400, detail="Invalid token. Reservation not confirmed.")
