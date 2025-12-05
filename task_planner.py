import calendar
import parlant.sdk as p
from contextlib import AsyncExitStack
from lagom import Container
from typing import Annotated
from enum import Enum
from datetime import datetime

from parlant.sdk import (
    PluginServer,
    ServiceRegistry,
    ToolContext,
    ToolParameterOptions,
    ToolResult,
    tool,
)


EXIT_STACK = AsyncExitStack()

class Subject(Enum):
    ARTS = "Art"
    BIOL = "Biology"
    CHEM = "Chemistry"
    ENGL = "English"
    GEOG = "Geography"
    HIST = "History"
    MATH = "Mathematics"
    MUST = "Music"
    PHYS = "Physics"
    LITE = "Literature"
    OTHER = "Other"

class Class(Enum):
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    ELEVEN = "11"
    TWELVE = "12"
    OTHER = "Other"

CLASS_LABELS = {
    Class.ONE: ["First Grade", "One"],
    Class.TWO: ["Second Grade", "Two"],
    Class.THREE: ["Third Grade", "Three"],
    Class.FOUR: ["Fourth Grade", "Four"],
    Class.FIVE: ["Fifth Grade", "Five"],
    Class.SIX: ["Sixth Grade", "Six"],
    Class.SEVEN: ["Seventh Grade", "Seven"],
    Class.EIGHT: ["Eighth Grade", "Eight"],
    Class.NINE: ["Ninth Grade", "Nine"],
    Class.TEN: ["Tenth Grade", "Ten"],
    Class.ELEVEN: ["Eleventh Grade", "Eleven"],
    Class.TWELVE: ["Twelfth Grade", "Twelve"]
}

class EducationalLevel(Enum):
    PRIMARY = "Primary"
    MIDDLE = "Middle"
    HIGH = "Higher"

class Semester(Enum):
    FIRST = "1"
    SECOND = "2"

SEMESTER_LABELS = {
    Semester.FIRST: ["First Semester", "First Term", "Term One", "Semester One"],
    Semester.SECOND: ["Second Semester", "Second Term", "Term Two", "Semester Two"]
}

@tool
async def free_days(context: ToolContext) -> ToolResult:
    return ToolResult(data=["Saturday", "Sunday"])

@tool
async def days_in_month(context: ToolContext, month: int, year: int) -> ToolResult:
    return ToolResult({"num_days": calendar.monthrange(year, month)[1]})

@tool
async def get_current_time(context:ToolContext) -> ToolResult:
    return ToolResult({"current_time": datetime.now().isoformat()})

@tool
async def get_educational_level(
    context: ToolContext,
    student_class: Annotated[Class, ToolParameterOptions(description="The class or grade level of the student", source="customer")],
) -> ToolResult:
    if Class.OTHER in [student_class]:
        return ToolResult(({"message": "Unsupported class. Please choose a different class in 1 - 12."}))
    if Class.ONE or Class.TWO or Class.THREE or Class.FOUR or Class.FIVE in [student_class]:
        return ToolResult(
            data={
                "educational_level": EducationalLevel.PRIMARY
            })
    elif Class.SIX or Class.SEVEN or Class.EIGHT or Class.NINE in [student_class]:
        return ToolResult(data={
            "educational_level": EducationalLevel.MIDDLE
        })
    else:
        return ToolResult(data={
            "educational_level": EducationalLevel.HIGH
        })

@tool
async def validate_subject(
    context: ToolContext,
    educational_level: Annotated[EducationalLevel, ToolParameterOptions(description="The educational level of the student", source="context")],
    subject: Annotated[Subject, ToolParameterOptions(description="The subject to validate", source="any")],
) -> ToolResult:
    if EducationalLevel.PRIMARY in [educational_level]:
        if Subject.ARTS or Subject.MATH or Subject.LITE or Subject.MUST in [subject]:
            return ToolResult(data={
                "subject": subject.value
                }, 
                message=f"The subject {subject.value} is valid for {educational_level.value} level."
            )
        else:   
            return ToolResult(message=f"The subject {subject.value} is not valid for {educational_level.value} level. Please choose another subject.")
    return ToolResult(data={
            "subject": subject.value
            }, 
            message=f"The subject {subject.value} is valid for {educational_level.value} level."
        )

@tool 
async def get_class_and_semester(
    context: ToolContext,
    student_class: Annotated[Class, ToolParameterOptions(description="The class or grade level of the student", source="customer")],
    semester: Annotated[Semester, ToolParameterOptions(description="The semester for which the task is planned", source="customer")],
) -> ToolResult:
    return ToolResult(
        data={
            "student_class": student_class.value,
            "semester": semester.value,
        }, 
        message= f"Class {student_class.value} and semester {semester.value} information retrieved successfully."
    )

@tool 
async def get_free_time_slots(
    context: ToolContext,
    duration_days: Annotated[int, ToolParameterOptions(description="The duration in days for the task", source="customer")],
    hour_per_day: Annotated[int, ToolParameterOptions(description="The number of hours per day to dedicate to the task", source="customer")],
) -> ToolResult:
    return ToolResult(
        data={
            "duration_days": duration_days,
            "hour_per_day": hour_per_day,
        },
        message=f"Free time slots for {duration_days} days with {hour_per_day} hours per day retrieved successfully."
    )

async def create_task_planner(agent: p.Agent) -> p.Journey:
    journey = await agent.create_journey(
        title="Task Planner Journey",
        description="A journey to help customers plan and organize their study schedules effectively.",
        conditions=["The customer requests help with study planning"],
    )

    t0 = await journey.initial_state.transition_to(chat_state="Ask the class level of the student in range 1 - 12.")

    t1 = await t0.target.transition_to(tool_state=get_educational_level)

    t2 = await t1.target.transition_to(chat_state="Ask the subject that the student wants to set study plan.")

    t3 = await t2.target.transition_to(tool_state=validate_subject)

    await t3.target.transition_to(state=p.END_JOURNEY)

PORT = 8199
TOOLS = [
    free_days,
    days_in_month,
    get_educational_level,
    validate_subject,
    get_free_time_slots
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
        name="task_planner",
        kind="sdk",
        url=f"http://{host}:{PORT}",
        transient=True,
    )

    await EXIT_STACK.enter_async_context(server)
    EXIT_STACK.push_async_callback(server.shutdown)


async def shutdown_module() -> None:
    await EXIT_STACK.aclose()

