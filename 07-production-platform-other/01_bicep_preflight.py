"""Lab 01 — locally validate Bicep platform assets; --apply provisions Azure."""
from scripts.preflight import entrypoint_main


if __name__ == "__main__":
    entrypoint_main("bicep")
