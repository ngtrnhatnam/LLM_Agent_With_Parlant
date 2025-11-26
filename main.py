from dotenv import load_dotenv
from learn_language import learn_languages
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
        description="You're a language agent who helps people learn language.",
    )

    await agent.create_guideline(
        condition="user greets",
        action="respond with a greeting, introduce yourself"
    )

    await agent.create_guideline(
        condition="the user wants to learn a language",
        action=[learn_languages],
    )

asyncio.run(main())