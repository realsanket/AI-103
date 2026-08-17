# Run: uv run python 08-advanced-agents-other/24_reminder_tool_preflight.py
"""Build the preview Reminder Toolbox tool and explain its runtime boundary.

Reminder is a connectionless Toolbox capability for hosted agents. It schedules
a follow-up in the same conversation from one minute through 43,200 minutes.
It is not an external calendar, durable workflow engine, or replacement for
Routines; the hosted agent/conversation lifecycle still governs delivery.

Flow:
  Default - build and print ReminderPreviewToolboxTool locally.

What to watch. Reminder is hosted-agent-only preview. Before use, define time
zone/user-expectation behavior, cancellation UX, retention, duplicate handling,
and what happens when the hosted agent or conversation is unavailable.

Prerequisites / env vars:
  None - this lesson makes no cloud call and creates no reminder
"""
from azure.ai.projects.models import ReminderPreviewToolboxTool


def reminder_tool() -> ReminderPreviewToolboxTool:
    return ReminderPreviewToolboxTool(
        name="follow-up-reminder",
        description=(
            "Schedule an approved follow-up in this conversation. "
            "Never infer a reminder without explicit user intent."
        ),
    )


def main() -> None:
    print("No cloud calls made.")
    print(f"- Tool payload: {reminder_tool().as_dict()}")
    print("- Preview; hosted agents only; connectionless.")
    print("- Supported delay documented as 1 through 43,200 minutes.")
    print("- Same-conversation follow-up, not an external calendar or Routine.")
    print("- Require explicit user intent and expose confirmation/cancellation behavior.")


if __name__ == "__main__":
    main()
