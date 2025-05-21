import asyncio
import json
import uuid
from typing import Any, Dict, List

import websockets

# Response type constants
TYPE_STATUS = "status"
TYPE_SOURCES = "sources"
TYPE_ANSWER = "answer"
STATUS_FINISHED = "finished"


class AskBillClient:
    """Client for interacting with the AskBill websocket service."""

    def __init__(self, uri):
        """
        Initialize the AskBill client.

        Args:
            uri: Websocket URI for the service
        """
        self.uri = uri
        # Generate UUIDs once at initialization
        self.anonymous_id = str(uuid.uuid4())
        self.user_id = str(uuid.uuid4())

    async def ask_question(
            self, question: str, timeout: float = 60.0
    ) -> Dict[str, Any]:
        """
        Send a question to the websocket service and return the complete response.

        Args:
            question: The question to ask
            timeout: Maximum time to wait for a response (seconds)

        Returns:
            Dictionary containing the answer and sources
        """
        full_answer: List[str] = []
        sources: List[Dict[str, Any]] = []

        try:
            # Add timeout to connection
            async with websockets.connect(
                    self.uri, ping_interval=30, ping_timeout=15, close_timeout=10
            ) as websocket:
                # Prepare the question message
                question_id = uuid.uuid4().hex[:12]
                question_message = {
                    "type": "question",
                    "anonymous_id": self.anonymous_id,
                    "user_id": self.user_id,
                    "question": question,
                    "question_id": question_id,
                    "chat_history": [],
                }

                # Send the question
                await websocket.send(json.dumps(question_message))

                # Create a task with timeout
                try:
                    async with asyncio.timeout(timeout):
                        # Listen for responses
                        while True:
                            response = await websocket.recv()
                            parsed_response = json.loads(response)
                            response_type = parsed_response.get("type")

                            if (
                                    response_type == TYPE_STATUS
                                    and parsed_response.get("status") == STATUS_FINISHED
                            ):
                                return {
                                    "answer": "".join(full_answer),
                                    "sources": sources,
                                }
                            elif response_type == TYPE_SOURCES:
                                sources = parsed_response.get("sources", [])
                            elif response_type == TYPE_ANSWER:
                                answer_part = parsed_response.get("ans", "")
                                if answer_part.strip():
                                    full_answer.append(answer_part)
                except asyncio.TimeoutError:
                    return {
                        "answer": "".join(full_answer)
                                  or f"Response timed out after {timeout} seconds.",
                        "sources": sources,
                    }
        except Exception as e:
            raise e
