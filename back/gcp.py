import asyncio
import enum
import inspect
import os
from re import S
import wave
from functools import wraps
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union, TypeVar, Generic, Type, AnyStr, Literal, get_origin, get_args
from typing_extensions import Annotated
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()
import logging
logger = logging.getLogger("gcp")

from google import genai
from google.genai import types

# Only run this block for Gemini Developer API
class GCP:
    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=os.getenv('GEMINI_API_KEY'),
            http_options=types.HttpOptions(api_version='v1alpha')
        )
        self.tools = []
        self.messages = []
        self.response_schema = None

    def config(self, system_message, response_schema = None, model = "gemini-2.5-flash"):
        self.system_message = system_message
        self.model = model
        self.response_schema = response_schema if response_schema else self.response_schema
        self.config=types.GenerateContentConfig(
            system_instruction=self.system_message,
            response_mime_type="application/json",
            response_schema=self.response_schema,
        ) if self.response_schema else types.GenerateContentConfig(
            system_instruction=self.system_message,
        )


    async def generate_stream(self, text: str):
        self.response_text = ""
        self.messages.append(types.Content(
            role="user",
            parts=[types.Part(text=text)]
        ))
        async for chunk in await self.client.aio.models.generate_content_stream(
            model=self.model,
            contents=self.messages,
            config=self.config
        ):
            self.response_text = f"{self.response_text}{chunk.text}"
            yield chunk.text


        self.messages.append(types.Content(
            role="model",
            parts=[types.Part(text=self.response_text)]
        ))

    
    def clean_response(self, response_text: str = None):
        text_to_use = response_text if response_text else self.response_text
        if self.response_schema:
            self.response_scheme = self.response_schema.model_validate_json(text_to_use)
            return self.response_scheme
        return text_to_use




# async def main():
#     gcp = GCP()
#     class CountrySchema(BaseModel):
#         name: str
#         long_essay: str
#     gcp.config("You are a helpful assistant that can answer questions and help with tasks.", CountrySchema)
    
#     # Consume the async generator
#     async for chunk in gcp.generate_stream("What is the capital of France?"):
#         print(chunk, end="", flush=True)
    
#     print("\n" + "="*50)
#     print("Final response:")
#     print(gcp.clean_response() if isinstance(gcp.clean_response(), str) else gcp.clean_response().model_dump_json())

# if __name__ == "__main__":
#     asyncio.run(main())