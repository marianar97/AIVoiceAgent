from __future__ import annotations
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm
)
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai
from dotenv import load_dotenv
from api import AssistantFnc
from prompts import WELCOME_MESSAGE, INSTRUCTIONS
import os
import logging

load_dotenv()

logger = logging.getLogger("myagent")
logger.setLevel(logging.INFO)

async def entrypoint(ctx: JobContext):
    logger.info("starting entrypoint")

    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()

    assistant_fnc = AssistantFnc()
    client_details = assistant_fnc.get_client_details()

    logger.info(f"!@# Client details: {client_details}")
    model = openai.realtime.RealtimeModel(
        instructions=INSTRUCTIONS.format(client_details=client_details),
        voice="shimmer",
        temperature=0.8,
        modalities=["audio", "text"],
    )

    assistant = MultimodalAgent(
        model=model,
        fnc_ctx=assistant_fnc
    )
    assistant.start(ctx.room)

    session = model.session[0]
    
    # Get client details with pending status at the start
    logger.info(f"Retrieved client details: {client_details}")
    
    # Add client context to conversation
    session.conversation.item.create(
        llm.ChatMessage(
            role="system",
            content=INSTRUCTIONS.format(client_details=client_details)
        )
    )

    session.response.create()

    @session.on("user_speech_committed")
    def on_user_speech_committed(msg: llm.ChatMessage):
        if isinstance(msg.content, list):
            msg.content = "\n".join("[image]" if isinstance(x, llm.ChatImage) else x for x in msg)
            
        handle_query(msg)
        
    def handle_query(msg: llm.ChatMessage):
        content = msg.content
        # Check if client confirms identity or says OK
        if isinstance(content, str) and any(keyword in content.lower() for keyword in ["ok", "yes", "correct", "that's me", "speaking"]):
            logger.info("Client confirmed identity or acknowledged call, marking as completed")
            assistant_fnc.mark_call_completed()
            
        session.conversation.item.create(
            llm.ChatMessage(
                role="user",
                content=content
            )
        )
        session.response.create()

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
