# learn_language.py
from contextlib import AsyncExitStack
from lagom import Container
from typing import Annotated
from enum import Enum

from parlant.sdk import (
    PluginServer,
    ServiceRegistry,
    ToolContext,
    ToolParameterOptions,
    ToolResult,
    tool,
)


EXIT_STACK = AsyncExitStack()

class Language(Enum):
    CHINESE = "zh"
    ENGLISH = "en"
    FRENCH = "fr" 
    GERMAN = "de"
    JAPANESE = "ja"
    RUSSIAN = "ru"
    SPANISH = "es"
    OTHER = "other"

@tool
async def learn_languages(
    context: ToolContext,
    language_to_learn: Annotated[Language, ToolParameterOptions(source="customer")],
) -> ToolResult:
    if language_to_learn.value == Language.OTHER:
        return ToolResult("This language is not supported. Please choose another language.")
    return ToolResult("Language selected successfully.")

PORT = 8199
TOOLS = [learn_languages]

async def initialize_module(container: Container) -> None:
    host = "127.0.0.1"

    server = PluginServer(
        tools=TOOLS,
        port=PORT,
        host=host,
        hosted=True,
    )

    await container[ServiceRegistry].update_tool_service(
        name="learn_language",
        kind="sdk",
        url=f"http://{host}:{PORT}",
        transient=True,
    )

    await EXIT_STACK.enter_async_context(server)
    EXIT_STACK.push_async_callback(server.shutdown)


async def shutdown_module() -> None:
    await EXIT_STACK.aclose()

