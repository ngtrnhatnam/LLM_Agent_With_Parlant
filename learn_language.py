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

# class Language(Enum):
#     CHINESE = "zh"
#     ENGLISH = "en"
#     FRENCH = "fr" 
#     GERMAN = "de"
#     JAPANESE = "ja"
#     RUSSIAN = "ru"
#     SPANISH = "es"
#     OTHER = "other"

# @tool
# async def learn_languages(
#     context: ToolContext,
#     language_to_learn: Annotated[Language, ToolParameterOptions(source="customer")],
# ) -> ToolResult:
#     if language_to_learn.value == Language.OTHER:
#         return ToolResult("This language is not supported. Please choose another language.")
#     return ToolResult("Language selected successfully.")

class Language(Enum):
    CHINESE = "zh"
    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"
    JAPANESE = "ja"
    RUSSIAN = "ru"
    SPANISH = "es"
    ARABIC = "ar"
    KOREAN = "ko"
    VIETNAMESE = "vi"
    OTHER = "other"

@tool
async def learn_languages(
    context: ToolContext,
    language_to_learn: Language,
) -> ToolResult:
    if language_to_learn == Language.OTHER:
        return ToolResult({"error": "unsupported_language"})

    return ToolResult({
        "status": "success",
        "message": f"You selected {language_to_learn.name}!"
    })

@tool
async def detect_language(
    context: ToolContext,
) -> ToolResult:
    text = context.input_text.lower()

    mapping = {
        "japanese": "ja",
        "arabic": "ar",
        "korean": "ko",
        "chinese": "zh",
        "english": "en",
        "spanish": "es",
        "french": "fr",
        "german": "de",
        "russian": "ru",
        "vietnamese": "vi",
    }

    for k, v in mapping.items():
        if k in text:
            return ToolResult({"language_code": v})

    return ToolResult({"language_code": "other"})


@tool
async def basic_greetings(
    context: ToolContext,
    language_code: str,
) -> ToolResult:
    greetings = {
        "ja": ["こんにちは (Konnichiwa)", "おはよう (Ohayou)", "こんばんは (Konbanwa)"],
        "en": ["Hello", "Hi", "Good morning"],
        "es": ["Hola", "Buenos días", "Buenas noches"],
        "fr": ["Bonjour", "Salut"],
        "de": ["Hallo", "Guten Tag"],
        "zh": ["你好 (Nǐ hǎo)", "早上好 (Zǎoshang hǎo)"],
        "ar": ["مرحبا (Marhaba)", "السلام عليكم (Assalamu Alaikum)"],
        "ko": ["안녕하세요 (Annyeonghaseyo)"],
        "vi": ["Xin chào", "Chào buổi sáng"],
    }

    return ToolResult({
        "greetings": greetings.get(language_code, [])
    })

@tool
async def basic_vocabulary(
    context: ToolContext,
    language_code: str,
) -> ToolResult:
    vocab = {
        "ja": {"water": "みず", "thank you": "ありがとう"},
        "en": {"water": "water", "thank you": "thank you"},
        "es": {"water": "agua", "thank you": "gracias"},
    }

    return ToolResult({
        "vocabulary": vocab.get(language_code, {})
    })

@tool
async def basic_grammar(
    context: ToolContext,
    language_code: str,
) -> ToolResult:
    grammar = {
        "ja": "Japanese uses SOV word order. Particles mark grammar functions.",
        "en": "English uses SVO word order. Tenses are heavily used.",
        "es": "Spanish verbs change (conjugate) according to the subject.",
    }

    return ToolResult({
        "grammar": grammar.get(language_code, "Grammar explanation unavailable.")
    })

@tool
async def pronunciation_help(
    context: ToolContext,
    language_code: str,
) -> ToolResult:
    rules = {
        "ja": "Japanese has consistent phonetics. Every vowel is pronounced.",
        "en": "English pronunciation is irregular. Many words are not phonetic.",
        "es": "Spanish pronunciation is mostly phonetic.",
    }

    return ToolResult({"pronunciation": rules.get(language_code, "")})

PORT = 8199
TOOLS = [
    detect_language,
    learn_languages,
    basic_greetings,
    basic_vocabulary,
    basic_grammar,
    pronunciation_help
]


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

