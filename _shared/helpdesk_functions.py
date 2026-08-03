"""Callable stubs backing the IT HelpDesk agent's function tools.

These are called by the app after the agent decides to invoke a tool. Kept
here (not inside a domain folder) because both Domain 2 (agents) and Domain 5
(RAG) lessons reference them.
"""


def get_password_reset_steps() -> str:
    return (
        "1. Go to https://accounts.northwind.internal/reset\n"
        "2. Enter your corporate email.\n"
        "3. Follow the link sent to your inbox (valid 15 min).\n"
        "4. Set a new password meeting the 12+ char + symbol policy."
    )


def get_vpn_troubleshooting_steps() -> str:
    return (
        "1. Confirm you are on Wi-Fi that permits UDP 443.\n"
        "2. Quit and relaunch the Northwind VPN client.\n"
        "3. Switch cluster to 'eu-west-b' if 'eu-west-a' times out.\n"
        "4. If MFA prompt loops, sign out of the client and sign back in.\n"
        "5. Still failing? Open a P2 ticket with ITSM."
    )


_SOFTWARE_GUIDES = {
    "slack": "Install via Company Portal → Slack (auto-configures SSO).",
    "zoom": "Install via Company Portal → Zoom Enterprise. Sign in via SSO.",
    "vs code": "Install via winget/brew or Company Portal. Enable Settings Sync.",
    "docker": "Install Docker Desktop. Enable Kubernetes only if requested by dev lead.",
}


def get_software_install_guide(software_name: str) -> str:
    return _SOFTWARE_GUIDES.get(
        software_name.lower(),
        f"No approved install guide for '{software_name}'. Open a ticket with IT.",
    )
