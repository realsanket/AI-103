def get_password_reset_steps() -> str:
    return (
        "To reset your password: "
        "1. Go to https://accounts.company.com/reset. "
        "2. Enter your company email address. "
        "3. Check your email for a reset link. The link expires in 15 minutes. "
        "4. Follow the link and choose a new password. "
        "5. If the link does not arrive, check your spam folder or contact IT."
    )


def get_vpn_troubleshooting_steps() -> str:
    return (
        "VPN troubleshooting steps: "
        "1. Confirm you are connected to the internet before launching the VPN client. "
        "2. Check that your VPN client is up to date. Version 4.2 or later is required. "
        "3. Try disconnecting and reconnecting. "
        "4. If the issue persists, restart your machine and try again. "
        "5. If you are on a public network, some ports may be blocked. Try a mobile hotspot. "
        "6. Contact IT if the problem continues after these steps."
    )


def get_software_install_guide(software_name: str) -> str:
    guides = {
        "slack": "To install Slack, visit https://slack.com/downloads, download the installer, and sign in with your company email.",
        "zoom": "To install Zoom, visit https://zoom.us/download, download Zoom Desktop Client, and sign in using SSO.",
        "vscode": "To install VS Code, visit https://code.visualstudio.com, download the installer, and follow the setup wizard.",
    }

    name = software_name.lower()

    return guides.get(
        name,
        f"No installation guide found for '{software_name}'. Please contact IT for assistance."
    )


def run_local_function(function_name: str, arguments: dict) -> str:
    if function_name == "get_password_reset_steps":
        return get_password_reset_steps()

    if function_name == "get_vpn_troubleshooting_steps":
        return get_vpn_troubleshooting_steps()

    if function_name == "get_software_install_guide":
        return get_software_install_guide(**arguments)

    return f"Unknown function requested: {function_name}"