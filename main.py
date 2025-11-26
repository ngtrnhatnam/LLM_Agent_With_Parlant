from dotenv import load_dotenv
from learn_language import *
import asyncio
import parlant.sdk as p
import os

load_dotenv()

async def main():   
  # If use Gemini/Ollama, then p.Server(nlp_service=p.NLPServices.gemini) / p.Server(nlp_service=p.NLPServices.ollama)
  # If use OpenAI, leave blank p.Server()
  async with p.Server(nlp_service=p.NLPServices.ollama) as server:

        agent = await server.create_agent(
            name="Stacy",
            description=(
                "You help users learn languages. "
                "Use the learn_languages tool when the user selects a language."
            ),
        )

        # Guideline 1 — greeting
        await agent.create_guideline(
            condition="the user greets",
            action="respond with a greeting and introduce yourself"
        )

        # Guideline 2 — user wants to learn a specific language
        await agent.create_guideline(
            condition=(
                "the user expresses a desire to learn a language, "
                "or mentions a target language such as Japanese, Chinese, English, etc."
            ),
            action=[learn_languages],
        )

        print("Agent created and guidelines registered! Ready to chat!")

        # Greeting guideline
        await agent.create_guideline(
            condition="the user greets or says hello",
            action="respond with a greeting and introduce yourself"
        )

        # Detect language guideline
        await agent.create_guideline(
            condition="the user writes a sentence and seems to ask what language it is, or asks to detect the language",
            action=[detect_language]
        )

        # Basic greetings guideline
        await agent.create_guideline(
            condition=(
                "the user asks how to say greetings in a specific language, "
                "or asks for simple everyday greetings such as hello, goodbye, thank you"
            ),
            action=[basic_greetings]
        )

        # Basic vocabulary guideline
        await agent.create_guideline(
            condition=(
                "the user asks for beginner vocabulary, common words, simple word lists, "
                "or says they want to learn basic words in a language"
            ),
            action=[basic_vocabulary]
        )

        # Basic grammar guideline
        await agent.create_guideline(
            condition=(
                'the user asks about grammar, sentence structure, conjugation, "how do I form sentences", '
                'or wants explanations of grammar rules'
            ),
            action=[basic_grammar]
        )

        # Pronunciation help guideline
        await agent.create_guideline(
            condition=(
                "the user asks how to pronounce a word or phrase, "
                "or says they cannot pronounce something correctly"
            ),
            action=[pronunciation_help]
        )

        # Learn languages (select language) guideline
        await agent.create_guideline(
            condition=(
                "the user expresses the desire to learn a language, wants to choose a language, "
                "or explicitly says they want to learn languages like Japanese, English, Chinese, etc."
            ),
            action=[learn_languages]
        )


asyncio.run(main())