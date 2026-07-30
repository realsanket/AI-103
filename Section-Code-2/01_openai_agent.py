import asyncio
from agents import Agent,function_tool,Runner

@function_tool
def get_password_reset_steps() -> str:
    """Returns the steps to reset a company account password."""
    return (
        "To reset your password: "
        "1. Go to https://accounts.company.com/reset. "
        "2. Enter your company email address. "
        "3. Check your email for a reset link (expires in 15 minutes). "
        "4. Follow the link and choose a new password. "
        "5. If the link does not arrive, check your spam folder or contact IT."
    )

@function_tool
def get_vpn_troubleshooting_steps() -> str:
    """Returns troubleshooting steps for VPN connection issues."""
    return (
        "VPN troubleshooting steps: "
        "1. Confirm you are connected to the internet before launching the VPN client. "
        "2. Check that your VPN client is up to date — version 4.2 or later is required. "
        "3. Try disconnecting and reconnecting. "
        "4. If the issue persists, restart your machine and try again. "
        "5. If you are on a public network, some ports may be blocked — try a mobile hotspot. "
        "6. Contact IT if the problem continues after these steps."
    )

@function_tool
def get_software_install_guide(software_name: str) -> str:
    """Returns installation instructions for a specified software package."""
    guides = {
        "slack": "To install Slack: visit https://slack.com/downloads, download the installer for your OS, and sign in with your company email.",
        "zoom": "To install Zoom: visit https://zoom.us/download, download Zoom Desktop Client, and sign in via SSO using your company domain.",
        "vscode": "To install VS Code: visit https://code.visualstudio.com, download the installer, and follow the setup wizard.",
    }
    name = software_name.lower()
    return guides.get(
        name,
        f"No installation guide found for '{software_name}'. Please contact IT for assistance."
    )

helpdesk_agent=Agent(
    name="IT Help Desk Agent",
    model="gpt-5.4-mini",
     instructions=(
        "You are a helpful IT support assistant for a company. "
        "When a user asks a question, use the available tools to find the answer. "
        "Always use a tool before responding — do not answer from memory alone. "
        "Keep your responses clear and concise."
    ),
    tools=[
        get_password_reset_steps,
        get_vpn_troubleshooting_steps,
        get_software_install_guide
    ]
)

async def main():
    queries = [
        "How do I reset my password?",
        "My VPN keeps disconnecting. What should I do?",
        "Can you tell me how to install Slack?",
    ]

    for query in queries:
        print(f"\nUser: {query}")
        result = await Runner.run(helpdesk_agent, input=query)
        print(f"Agent: {result.final_output}")

if __name__ == "__main__":
    asyncio.run(main())