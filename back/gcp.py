import asyncio
import enum
import inspect
import os
import wave
from functools import wraps
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union, TypeVar, Generic, Type, AnyStr, Literal, get_origin, get_args
from typing_extensions import Annotated

from pydantic import BaseModel

import numpy as np
from utils.decor import log_decor
from google.genai import types
from google import genai
# from google.cloud.aiplatform_v1beta1.types import content  # Commented out due to ImportError
from vertexai.generative_models import (
    GenerativeModel,
    Part,
    ChatSession,
    Content,
    GenerationConfig,
    GenerationResponse,
    HarmCategory,
    HarmBlockThreshold,
    Image,
)
from vertexai.generative_models._generative_models import ResponseBlockedError

from dotenv import load_dotenv

from ai.models import Agent, AgentSchema
from ai.llm.search import SearchManager

load_dotenv()
import logging
logger = logging.getLogger("gcp")


class TextDataPart(BaseModel):
    """Represents a text data part."""

    text: str

    def model_dump_gcp(self, *args, **kwargs):
        """Convert the TextDataPart to a Part object."""
        return Part.from_text(self.text)

    def model_dump(self, *args, **kwargs):
        """Convert the TextDataPart to a dictionary."""
        return self.text


class BlobDataPart(BaseModel):
    """Represents a blob data part."""

    blob: bytes
    mime_type: str

    def model_dump_gcp(self, *args, **kwargs):
        """Convert the BlobDataPart to a dictionary."""
        return Part.from_bytes(
            {
                "blob": self.blob,
                "mime_type": self.mime_type,
            }
        )
    



class LinkDataPart(BaseModel):
    """Represents a link data part."""

    url: str
    mime_type: str

    def model_dump_gcp(self, *args, **kwargs):
        """Convert the LinkDataPart to a dictionary."""
        return Part.from_uri(
            {
                "url": self.url,
                "mime_type": self.mime_type,
            }
        )


class DataPart(BaseModel):
    """Represents a part of a data object."""

    data: Union[TextDataPart, BlobDataPart, LinkDataPart]

    def model_dump(self, *args, **kwargs):
        """Convert the DataPart to a dictionary."""
        return [data.model_dump(*args, **kwargs) for data in self.data]

    def model_dump_gcp(self, *args, **kwargs):
        return self.data.model_dump_gcp(*args, **kwargs)
    

class Modality(enum.Enum):
    """Enum for modalities."""

    TEXT = "text"
    LIVE = "live"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


MessageType = TypeVar('MessageType', str, Dict[str, Any], BaseModel, TextDataPart, BlobDataPart, LinkDataPart, DataPart)
MessageContent = Union[str, Dict[str, Any], BaseModel, TextDataPart, BlobDataPart, LinkDataPart, DataPart, List[Union[str, Dict[str, Any]]]]

class GCP(Generic[MessageType]):
    @log_decor(mode=1)
    def __init__(self, model: str = "gemini-2.0-flash-lite-001", 
                 system_prompt: Optional[str] = None, 
                 config: Optional[types.GenerateContentConfig] = None, 
                 history: Optional[List[Union[MessageContent, types.Content]]] = None, 
                 **kwargs):

        self.system_prompt = system_prompt
        self.config = config
        if self.config is None:
            self.config = types.GenerateContentConfig(**kwargs) if not system_prompt else types.GenerateContentConfig(system_instruction=system_prompt, **kwargs)
        # self.client  = genai.Client(
        #     vertexai=True, project=os.getenv('GOOGLE_CLOUD_PROJECT'), location=os.getenv('GOOGLE_CLOUD_LOCATION')
        # )
        self.model = model
        self.history = history
        self.client = genai.Client(
            vertexai=True,
            project="weighty-archive-456713-q6",
            location="global",
        )
        self.response = []


    def _validate_message(self, message: MessageContent) -> types.Content:
        """Validate and convert message to GCP Content type."""
        if isinstance(message, str):
            return types.Content(role="user", parts=[types.Part(text=message)])
        elif isinstance(message, dict):
            return types.Content(**message)
        elif hasattr(message, 'model_dump_gcp'):
            return message.model_dump_gcp()
        elif isinstance(message, list):
            parts = []
            for item in message:
                if isinstance(item, str):
                    parts.append(types.Part.from_text(text=item))
                elif isinstance(item, dict):
                    parts.append(types.Part(**item))
                elif hasattr(item, 'model_dump_gcp'):
                    parts.append(item.model_dump_gcp())
            return types.Content(role="user", parts=parts)
        raise ValueError(f"Unsupported message type: {type(message)}")

    @log_decor
    async def generate_stream(self, contents: Union[MessageContent, List[MessageContent]], model_id: str = 'gemini-2.0-flash-lite-001'):
        """Generate a streaming response from the model.
        
        Args:
            contents: Can be a string, dict, Pydantic model, or list of these
            model_id: The model ID to use for generation
            
        Yields:
            Response chunks from the model
        """
        if not isinstance(contents, list):
            contents = [contents]
            
        validated_contents = [self._validate_message(msg) for msg in contents]
        stream = await self.client.aio.models.generate_content_stream(
            model=model_id,
            contents=validated_contents,
            config=self.config,
        )
        async for response in stream:
            yield response


    @log_decor
    async def send_stream(self, message: MessageContent, config: Optional[types.GenerateContentConfig] = None):
        """Send a message to the chat.
        """
        self.response = []
        validated_msg = self._validate_message(message)
        self.history.append(validated_msg)
        stream = await self.client.aio.models.generate_content_stream(
            model=self.model,
            contents=self.history,
            config=self.config if config is None else config,
        )
        async for response in stream:
            self._process_response(response)
            yield response
        
        self._update_history()


    @log_decor
    def _update_history(self):
        self.history.append(types.Content(role="model", parts=self.response))

    @log_decor
    def _process_response(self, response):
        self.response.append(response)

        





    @log_decor
    def get_history(self):
        return self.history

class GCPChat(Generic[MessageType]):
    @log_decor
    def __init__(self, model: str = "gemini-2.5-pro-preview-05-06", 
                 system_prompt: Optional[str] = None, 
                 config: Optional[types.GenerateContentConfig] = None, 
                 history: Optional[List[Union[MessageContent, types.Content]]] = None, 
                 **kwargs):
        """Initialize GCPChat with model, system prompt, and configuration.
        
        Args:
            model: The model ID to use for chat
            system_prompt: Optional system prompt for the chat
            config: Optional configuration for content generation
            history: Optional chat history to initialize with
            **kwargs: Additional arguments to pass to GenerateContentConfig
        """
        self.system_prompt = system_prompt
        self.config = config
        if self.config is None:
            self.config = types.GenerateContentConfig(
                **kwargs if not system_prompt 
                else {**{"system_instruction": system_prompt}, **kwargs}
            )
            
        self.client = genai.Client(
            vertexai=True,
            project="weighty-archive-456713-q6",
            location="global",
        )
        self.model = model
        
        # Store and validate history
        self._history: List[types.Content] = []
        if history:
            self._validated_msg = self._validate_message(history)
            self.chat = self.client.aio.chats.create(
                model=model,
                config=self.config,
                history=validated_msg
            )
        else:
            self.chat = self.client.aio.chats.create(
                model=model,
                config=self.config
            )


    @log_decor
    def _validate_message(self, message: MessageContent) -> Union[str, types.Part, Dict]:
        """Validate and convert message to a format compatible with Gemini SDK.
        
        Returns:
            A string, Part object, or dictionary that can be used with Gemini SDK
        """
        if isinstance(message, str):
            return message
        elif isinstance(message, dict):
            return message
        elif hasattr(message, 'model_dump_gcp'):
            return message.model_dump_gcp()
        elif isinstance(message, list):
            # For lists, we'll return the first item's content if it's a single text message
            if len(message) == 1 and isinstance(message[0], str):
                return message[0]
            # For more complex messages, convert to a format Gemini can handle
            parts = []
            for item in message:
                if isinstance(item, str):
                    parts.append(types.Part.from_text(text=item))
                elif isinstance(item, dict):
                    parts.append(types.Part(**item))
                elif hasattr(item, 'model_dump_gcp'):
                    parts.append(item.model_dump_gcp())
            return {"parts": parts, "role": "user"}
        raise ValueError(f"Unsupported message type: {type(message)}")

    @log_decor
    async def send(self, message: MessageContent, config: Optional[types.GenerateContentConfig] = None):
        """Send a message to the chat.
        
        Args:
            message: The message to send. Can be a string, dict, Pydantic model, or list of these
            config: Optional config to override the default config
            
        Returns:
            The response from the model
        """
        if not self.chat:
            raise RuntimeError("Chat session not initialized")
            
        validated_message = self._validate_message(message)
        return await self.chat.send_message(validated_message, config) if config else await self.chat.send_message(validated_message)

    @log_decor
    async def send_stream(self, message: MessageContent, config: Optional[types.GenerateContentConfig] = None):
        """Send a message to the chat and stream the response.
        
        Args:
            message: The message to send. Can be a string, dict, Pydantic model, or list of these
            config: Optional config to override the default config
            
        Yields:
            Response chunks from the model
        """
        if not self.chat:
            raise RuntimeError("Chat session not initialized")
            
        # logger.info(f"Sending message: {message}")
        validated_message = self._validate_message(message)
        # logger.info(f"Validated message: {validated_message}")
        stream = await self.chat.send_message_stream(validated_message, config) if config else await self.chat.send_message_stream(validated_message)
        async for chunk in stream:
            yield chunk
        # yield {"history" : self.chat.get_history()}


    @log_decor
    def get_history(self):
        return self.chat.get_history()



class GCPAgentCreate(GCP):

    async def create_agent(self, name:str, description:str, policy:str):
        """Function to create an agent. To be used once the agent details are finalized."""
        agent = await Agent.create_agent(self.user, name, description, policy)
        self.agent = agent
        return AgentSchema.model_validate(agent)


    async def edit_agent(self, name: Optional[str] = None, description: Optional[str] = None, policy: Optional[str] = None):
        """Function to edit an agent. To be used once the agent details are finalized."""
        agent = await Agent.objects.aget(id=self.agent.id)
        if name:
            agent.name = name
        if description:
            agent.description = description
        if policy:
            agent.policy = policy
        await agent.asave()
        return AgentSchema.model_validate(agent)
    

    async def extract_content(self, url:str):
        async with SearchManager() as search_manager:
            return await search_manager.extract_content(url)
        

    @log_decor
    def __init__(self, user,history=None, **kwargs):
        self.system_prompt = "You are an expert at creating agents for people, by proactively interacting with the users and figuring out what agents they want to build.\
            Once you have figured out what the user wants to do, you will formulate the description and policy for the agent.\
            The description should be concise and easy to understand.\
            The policy should be concise and easy to understand.\
            Once you have formulated the description and policy, validate the same with the user.\
            If the user is satisfied with the description and policy, enquire with the user on any name they want to give to the agent.\
            Generate an apt name for the agent, if the user doesn't provide a name.\
            Finally use the create_agent method to create the agent.\
            Subsequently, if the user asks for any changes to the agent, use the edit_agent method to edit the agent.\
            Upon completion of the agent creation process or the editing process, ask the user to check out the agent for a preview on the right next tab.\
            Add the name of the agent and the description as part of the policy as who and what this agent is.\
            "
        
        self.user = user
        config = types.GenerateContentConfig(
            system_instruction=self.system_prompt,
            tools=[self.create_agent, self.edit_agent, self.extract_content]
        )
        self.agent = None
        super().__init__(system_prompt=self.system_prompt, config=config,history=history, **kwargs)
        self.agent = None


class GCPLive(GCP[MessageType]):
    """A class for interacting with Google's live chat API.
    
    This class provides methods for real-time interaction with Google's live chat models,
    supporting both turn-based and real-time input modes.
    """
    
    @log_decor
    def __init__(self, model: str = "gemini-2.0-flash-live-001",
                 system_prompt: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None,
                 **kwargs):
        """Initialize GCPLive with model and configuration.
        
        Args:
            model: The model ID to use for live chat (default: gemini-2.0-flash-live-001)
            system_prompt: Optional system prompt for the chat
            config: Optional configuration dictionary for the live session
            **kwargs: Additional arguments to pass to the configuration
        """
        self.model = model
        self.system_prompt = system_prompt
        self.config = config or {}
        
        # Initialize client
        self.client = genai.Client(
            vertexai=True,
            project="weighty-archive-456713-q6",
            location="global",
        )
        
        # Initialize session
        self.session = None
        
        # Set up config with default values if not provided
        if "response_modalities" not in self.config:
            self.config["response_modalities"] = ["TEXT"]
            
        # Add system prompt to config if provided
        if system_prompt:
            self.config["system_instruction"] = system_prompt
            
        # Update config with any additional kwargs
        self.config.update(kwargs)
    
    async def __aenter__(self):
        """Context manager entry point."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        await self.close()
    
    async def connect(self):
        """Establish a connection to the live chat session."""
        if self.session is None:
            self.session = await self.client.aio.live.connect(
                model=self.model,
                config=self.config
            )
        return self.session
    
    async def close(self):
        """Close the live chat session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _validate_content(self, content: Any) -> types.Content:
        """Validate and convert content to GCP Content type."""
        if isinstance(content, types.Content):
            return content
        elif isinstance(content, dict):
            return types.Content(**content)
        elif isinstance(content, str):
            return types.Content(role="user", parts=[types.Part(text=content)])
        elif hasattr(content, 'model_dump_gcp'):
            return content.model_dump_gcp()
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")
    
    async def send_client_content(self, *, turns: Optional[Union[types.Content, List[types.Content]]] = None, 
                               turn_complete: bool = True):
        """Send non-realtime, turn-based content to the model.
        
        Args:
            turns: A Content object or list of Content objects (or equivalent dicts)
            turn_complete: If True (default), the model will reply immediately. If False, 
                          the model will wait for additional content before responding.
                          
        Returns:
            None
        """
        if self.session is None:
            await self.connect()
            
        if turns is not None:
            if not isinstance(turns, list):
                turns = [turns]
                
            validated_turns = [self._validate_content(turn) for turn in turns]
            await self.session.send_client_content(turns=validated_turns, turn_complete=turn_complete)
    
    async def send_stream(self, *, media=None, audio=None, audio_stream_end=None, 
                               video=None, text=None, activity_start=None, activity_end=None):
        """Send realtime input to the model.
        
        Args:
            media: A Blob-like object, the realtime media to send
            audio: Audio data to send
            audio_stream_end: Flag indicating end of audio stream
            video: Video data to send
            text: Text to send
            activity_start: Flag indicating start of user activity
            activity_end: Flag indicating end of user activity
            
        Returns:
            None
        """
        if self.session is None:
            await self.connect()
            
        await self.session.send_realtime_input(
            media=media,
            audio=audio,
            audio_stream_end=audio_stream_end,
            video=video,
            text=text,
            activity_start=activity_start,
            activity_end=activity_end
        )
    
    async def send_tool_response(self, function_responses):
        """Send a tool response to the model.
        
        Args:
            function_responses: The function response(s) to send
            
        Returns:
            None
        """
        if self.session is None:
            await self.connect()
            
        await self.session.send_tool_response(function_responses=function_responses)
    
    async def receive(self):
        """Receive messages from the live session.
        
        Yields:
            Messages from the model
        """
        if self.session is None:
            await self.connect()
            
        async for msg in self.session.receive():
            yield msg


if __name__ == "__main__":
    gcp = GCP()
    @log_decor
    async def main():
        async for response in gcp.generate("Hello, world!"):
            print(response.text)
    asyncio.run(main())
