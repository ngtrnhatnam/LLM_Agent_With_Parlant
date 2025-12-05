import asyncio
from task_planner import (
    free_days,
    days_in_month,
    get_educational_level,
    validate_subject,
    get_free_time_slots,
    create_task_planner
)
import parlant.sdk as p

async def main():
  # If use Gemini/Ollama, then p.Server(nlp_service=p.NLPServices.gemini) / p.Server(nlp_service=p.NLPServices.ollama)
  # If use OpenAI, leave blank p.Server()
  async with p.Server(nlp_service=p.NLPServices.ollama) as server:
    agent = await server.create_agent(
        name="Otto Carmen",
        description="You are a study advisor, helping users plan, organize study schedules and find relevant materials.",
        tags = ["study advisor", "task planner"]
    )
    
    customer = await server.create_customer(
        name="Nam",
        tags=["student", "customer"],
    )   

    await create_task_planner(agent)

    await agent.create_guideline(
        condition="The customer greets you without any specifying any particular need",
        action="greet them back and introduce yourself as a study advisor, offering help with planning and organizing study schedules.",
    )

asyncio.run(main())