from livekit.agents import llm
import enum
from db import DB
import logging
from typing import Annotated

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
    
    def get_client_details_str(self) -> str:
        logger.info(f"Getting client details")
        return f"The client details are: {self.get_client_str()}"
        
    def has_profile(self) -> bool:
        return self._client_details[ClientDetails.NAME] != ""
