# Run: uv run python 01-plan-and-manage/01_model_catalog_list.py
"""List the deployments that exist in your Foundry project.

Beginner note:
  A "deployment" is a named copy of a model you can call. The MODEL is the
  brains (gpt-5-mini, text-embedding-3-large); the DEPLOYMENT is the
  addressable endpoint you send requests to. Same model can be deployed many
  times under different names, quotas, and regions.

  This is your live model catalog — every other lesson in this domain sends
  requests to one of these deployment names.

What to watch:
  - `name` column = what you pass as the `model=` argument in later lessons.
  - `model` column = the underlying model powering that deployment.
  - `type` column = the SKU (GlobalStandard, DataZoneStandard, PTU, ...).
"""
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
