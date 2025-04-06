from livekit.agents import llm
import enum
from db import DB
import logging
from typing import Annotated

logger = logging.getLogger("api")
logger.setLevel(logging.INFO)

class ClientDetails(enum.Enum):
    NAME = "name"
    DEBT = "debt"
    PAY_DATE = "pay_date"
    CALL_STATUS = "call_status"

class AssistantFnc(llm.FunctionContext):
    def __init__(self):

        super().__init__()
        
        self._client_details = {
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
        result = self.db.get_client()
        logger.info(f"!@# Client Result: {result}")
        if result:
            self._client_details[ClientDetails.NAME] = result[0]
            self._client_details[ClientDetails.DEBT] = result[1]
            self._client_details[ClientDetails.PAY_DATE] = result[2]
            self._client_details[ClientDetails.CALL_STATUS] = result[3]

        return f"The client details are: {self.get_client_str()}"
    
    def get_client_details_str(self) -> str:
        logger.info(f"Getting client details")
        return f"The client details are: {self.get_client_str()}"
        
    def has_profile(self) -> bool:
        return self._client_details[ClientDetails.NAME] != ""
