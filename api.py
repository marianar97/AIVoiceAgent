from livekit.agents import llm
import enum
from db import DB
import logging
from typing import Annotated
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from email.message import EmailMessage
import smtplib, ssl
from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger("api")
logger.setLevel(logging.INFO)

class ClientDetails(enum.Enum):
    ID = "id"
    NAME = "name"
    DEBT = "debt"
    PAY_DATE = "pay_date"
    CALL_STATUS = "call_status"

class AssistantFnc(llm.FunctionContext):
    def __init__(self):

        super().__init__()
        
        self._client_details = {
            ClientDetails.ID: None,
            ClientDetails.NAME: "",
            ClientDetails.DEBT: "",
            ClientDetails.PAY_DATE: "",
            ClientDetails.CALL_STATUS: ""
        }
        self.db = DB()

        logger.info(f"!@# AssistantFnc initialized")
    
    def get_client_str(self) -> str:
        car_str = []
        for key, value in self._client_details.items():
            car_str.append(f"{key}: {value}")
        return "\n".join(car_str)

    @llm.ai_callable(name="get_client_details", description="Get details of a client from the database where status is pending")
    def get_client_details(self):
        """
        Retrieves a client details from the database where status is pending.
        
        Returns:
            A string containing the formatted client details
        """
        client = self.db.get_client()
        logger.info(f"!@# Client Result: {client}")
        if client:
            self._client_details[ClientDetails.ID] = client.id
            self._client_details[ClientDetails.NAME] = client.name
            self._client_details[ClientDetails.DEBT] = client.debt
            self._client_details[ClientDetails.PAY_DATE] = client.pay_date
            self._client_details[ClientDetails.CALL_STATUS] = client.call_status
            return f"The client details are: {self.get_client_str()}"
        else:
            return "No client found"
    
    @llm.ai_callable(name="mark_call_completed", description="Mark the current client's call status as completed")
    def mark_call_completed(self):
        """
        Updates the current client's call status to 'completed' in the database.
        
        Returns:
            A confirmation message
        """
        if self._client_details[ClientDetails.ID]:
            success = self.db.update_client_status(self._client_details[ClientDetails.ID], "completed")
            if success:
                self._client_details[ClientDetails.CALL_STATUS] = "completed"
                logger.info(f"Client {self._client_details[ClientDetails.ID]} marked as completed")
                return "Client call status updated to completed successfully"
            else:
                logger.error(f"Failed to update client {self._client_details[ClientDetails.ID]} status")
                return "Failed to update client status"
        else:
            logger.error("No client ID available to update status")
            return "No active client found to update status"
    
    @llm.ai_callable(name="create_follow_up_reminder", description="Create a follow-up reminder call with a new due date")
    def create_follow_up_reminder(self, new_pay_date: str):
        """
        Creates a new follow-up reminder call record with the same client information but a new due date.
        
        Args:
            new_pay_date: The new payment due date (e.g., "June 30")
            
        Returns:
            A confirmation message
        """
        if not self._client_details[ClientDetails.ID]:
            logger.error("No active client to create follow-up reminder for")
            return "Cannot create follow-up reminder: No active client found"
            
        client_name = self._client_details[ClientDetails.NAME]
        debt = self._client_details[ClientDetails.DEBT]
        
        try:
            new_id = self.db.create_follow_up_reminder(client_name, debt, new_pay_date)
            logger.info(f"Created follow-up reminder for client {client_name} with new due date {new_pay_date}, ID: {new_id}")
            return f"Follow-up reminder created successfully. We will call {client_name} again before {new_pay_date} about their ${debt} debt."
        except Exception as e:
            logger.error(f"Failed to create follow-up reminder: {str(e)}")
            return f"Failed to schedule follow-up reminder: {str(e)}"
    
    @llm.ai_callable(name="send_email_reminder", description="Send an email reminder to the client")
    def send_email_reminder(self, email_address: str, reminder_date: str):
        """
        Sends an email reminder to the client about their outstanding debt.
        
        Args:
            email_address: The client's email address
            reminder_date: The reminder date
            
        Returns:
            A confirmation message
        """

        if not self._client_details[ClientDetails.ID]:
            logger.error("No active client to send email reminder to")
            return "Cannot send email reminder: No active client found"
            
        client_name = self._client_details[ClientDetails.NAME]
        debt = self._client_details[ClientDetails.DEBT]
        pay_date = reminder_date if reminder_date else self._client_details[ClientDetails.PAY_DATE]
        
        # Create email content
        body = f"""
            Dear {client_name},

            This is a friendly reminder about your outstanding payment of ${debt} due on {pay_date}.

            Please ensure your payment is made before the due date to avoid any late fees or penalties.

            If you have any questions or need to discuss payment options, please contact our customer service at (555) 123-4567.

            Thank you for your attention to this matter.

            Sincerely,
            DocBank Payment Services
        """
        smtp_server = "smtp.gmail.com"
        port = 465  # For SSL
        sender_email = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("EMAIL_PASSWORD")

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, email_address, body)
            logger.info(f"Email sent to {email_address}")
            return "Email sent successfully"
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return f"Failed to send email: {str(e)}"


    def get_client_details_str(self) -> str:
        logger.info(f"Getting client details")
        return f"The client details are: {self.get_client_str()}"
        
    def has_profile(self) -> bool:
        return self._client_details[ClientDetails.NAME] != ""
