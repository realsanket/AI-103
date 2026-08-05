"""Lab 05 — locally validate diagnostic configuration; no automated apply."""
from scripts.preflight import entrypoint_main


if __name__ == "__main__":
    entrypoint_main("diagnostics")
