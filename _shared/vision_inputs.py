"""Local validation and encoding for vision lesson inputs."""
import base64
from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError

_MIME_TYPES = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}


def _image(path: Path, label: str) -> tuple[str, tuple[int, int], str]:
    if not path.is_file():
        raise ValueError(f"{label} does not exist: {path}")
    try:
        with Image.open(path) as opened:
            opened.verify()
        with Image.open(path) as opened:
            image_format = opened.format
            size = opened.size
            mode = opened.mode
    except (OSError, UnidentifiedImageError) as error:
        raise ValueError(f"{label} is not a readable image: {path}") from error
    if image_format not in _MIME_TYPES:
        raise ValueError(f"{label} must be PNG, JPEG, or WEBP: {path}")
    return image_format, size, mode


def image_data_url(path: Path) -> str:
    """Return a model-ready data URL after checking a local image."""
    image_format, _, _ = _image(path, "image")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{_MIME_TYPES[image_format]};base64,{encoded}"


def validate_edit_inputs(image_path: Path, mask_path: Path | None = None) -> None:
    """Check image-edit inputs before opening a cloud client."""
    _, image_size, _ = _image(image_path, "source image")
    if mask_path is None:
        return
    mask_format, mask_size, mask_mode = _image(mask_path, "mask")
    if mask_format != "PNG":
        raise ValueError(f"mask must be PNG: {mask_path}")
    if mask_size != image_size:
        raise ValueError(
            f"mask dimensions {mask_size} must match source image dimensions {image_size}"
        )
    if "A" not in mask_mode:
        raise ValueError(f"mask must contain an alpha channel: {mask_path}")
    with Image.open(mask_path) as mask:
        alpha = mask.getchannel("A")
        if alpha.getextrema()[0] == 255:
            raise ValueError(f"mask has no transparent editable pixels: {mask_path}")


def save_generated_image(response: object, destination: Path) -> None:
    """Validate returned base64 image bytes before replacing lesson output."""
    try:
        encoded = response.data[0].b64_json  # type: ignore[attr-defined]
        image_bytes = base64.b64decode(encoded, validate=True)
        with Image.open(BytesIO(image_bytes)) as image:
            image.verify()
    except (AttributeError, IndexError, TypeError, ValueError, OSError, UnidentifiedImageError) as error:
        raise RuntimeError("Image API response did not contain a valid base64 image.") from error
    destination.write_bytes(image_bytes)
