
import os
import secrets
import smtplib
import bcrypt

from email.message import EmailMessage
from dotenv import load_dotenv

from modules.database import get_connection

load_dotenv()


def register_user(username, email, password):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        cursor.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
        """, (username, email.lower(), password_hash.decode("utf-8")))

        connection.commit()
        return True, "Registration successful."

    except Exception as error:
        if getattr(error, "errno", None) == 1062:
            return False, "Email already registered."

        return False, "Registration failed. Check database connection."

    finally:
        cursor.close()
        connection.close()


def login_user(email, password):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email.lower(),)
        )

        user = cursor.fetchone()

        if user is None:
            return None

        is_valid = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        )

        if is_valid:
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"]
            }

        return None

    finally:
        cursor.close()
        connection.close()


def send_password_reset_otp(email):
    email = email.strip().lower()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        user = cursor.fetchone()

        # Same response is used whether the email exists or not.
        if user is None:
            return False

        user_id = user["id"]

        # Allow only one OTP request per minute.
        cursor.execute("""
            SELECT id
            FROM password_reset_otps
            WHERE user_id = %s
              AND created_at >= DATE_SUB(NOW(), INTERVAL 1 MINUTE)
            LIMIT 1
        """, (user_id,))

        recent_request = cursor.fetchone()

        if recent_request:
            return False

        otp = str(secrets.randbelow(900000) + 100000)

        otp_hash = bcrypt.hashpw(
            otp.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # Gmail configuration from .env
        sender_email = os.getenv("EMAIL_ADDRESS")
        app_password = os.getenv("EMAIL_APP_PASSWORD")

        if not sender_email or not app_password:
            return False

        message = EmailMessage()
        message["Subject"] = "AI Excel Analyst - Password Reset OTP"
        message["From"] = sender_email
        message["To"] = email

        message.set_content(f"""
Hello,

Your password reset OTP is: {otp}

This OTP is valid for 10 minutes.

Do not share this OTP with anyone.

If you did not request a password reset, ignore this email.

AI Excel Analyst Team
""")

        # Send OTP through Gmail SMTP
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password.replace(" ", ""))
            server.send_message(message)

        # Save OTP hash only after email is sent successfully.
        cursor.execute("""
            INSERT INTO password_reset_otps
            (user_id, otp_hash, expires_at)
            VALUES (
                %s,
                %s,
                DATE_ADD(NOW(), INTERVAL 10 MINUTE)
            )
        """, (user_id, otp_hash))

        connection.commit()
        return True

    except Exception as error:
        connection.rollback()
        print("OTP EMAIL ERROR:", repr(error))
        return False

    finally:
        cursor.close()
        connection.close()


def reset_password(email, otp, new_password):
    email = email.strip().lower()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        user = cursor.fetchone()

        if user is None:
            return False, "Invalid or expired OTP."

        user_id = user["id"]

        cursor.execute("""
            SELECT *
            FROM password_reset_otps
            WHERE user_id = %s
              AND used = 0
              AND expires_at > NOW()
              AND attempts < 5
            ORDER BY id DESC
            LIMIT 1
        """, (user_id,))

        reset_record = cursor.fetchone()

        if reset_record is None:
            return False, "OTP is invalid, expired, or already used."

        is_valid = bcrypt.checkpw(
            otp.encode("utf-8"),
            reset_record["otp_hash"].encode("utf-8")
        )

        if not is_valid:
            cursor.execute("""
                UPDATE password_reset_otps
                SET attempts = attempts + 1
                WHERE id = %s
            """, (reset_record["id"],))

            connection.commit()
            return False, "Incorrect OTP. Please try again."

        # Hash the new password using bcrypt.
        new_password_hash = bcrypt.hashpw(
            new_password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        cursor.execute("""
            UPDATE users
            SET password_hash = %s
            WHERE id = %s
        """, (new_password_hash, user_id))

        # Mark all existing reset OTPs as used.
        cursor.execute("""
            UPDATE password_reset_otps
            SET used = 1
            WHERE user_id = %s
        """, (user_id,))

        connection.commit()

        return True, "Password reset successful. Please login."

    except Exception:
        connection.rollback()
        return False, "Password reset failed. Please try again."

    finally:
        cursor.close()
        connection.close()
