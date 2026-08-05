"""Lab 02 — locally validate Terraform platform assets; --apply provisions Azure."""
from scripts.preflight import entrypoint_main


if __name__ == "__main__":
    entrypoint_main("terraform")
