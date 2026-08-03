"""List available deployments — treat as your live "model catalog" reference."""
from _shared.foundry_client import project_client


def main() -> None:
    client = project_client()
    print(f"{'name':<32} {'model':<28} {'type':<20}")
    print("-" * 82)
    for d in client.deployments.list():
        # `d` shape varies by SDK version — surface the common fields defensively.
        name = getattr(d, "name", None) or getattr(d, "id", "?")
        model = getattr(d, "model_name", None) or getattr(getattr(d, "properties", None), "model", "?")
        d_type = getattr(d, "type", None) or getattr(d, "sku_name", "?")
        print(f"{str(name):<32} {str(model):<28} {str(d_type):<20}")


if __name__ == "__main__":
    main()
