from pathlib import Path
from uuid import uuid4

import requests
from PIL import Image

from app.config import settings


_pipeline = None


def _get_local_pipeline():
    global _pipeline

    if _pipeline is not None:
        return _pipeline

    import torch
    from diffusers import StableDiffusionPipeline

    dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    kwargs = {
        "torch_dtype": dtype,
    }

    if torch.cuda.is_available():
        kwargs["variant"] = "fp16"

    _pipeline = StableDiffusionPipeline.from_pretrained(
        settings.local_image_model,
        **kwargs,
    )

    if torch.cuda.is_available():
        _pipeline = _pipeline.to("cuda")
    else:
        _pipeline = _pipeline.to("cpu")

    return _pipeline


def generate_image(
    prompt: str,
    filename_prefix: str = "panel",
) -> str:

    filename = (
        f"{filename_prefix}_{uuid4().hex[:10]}.png"
    )

    output_path = settings.panels_dir / filename

    provider = settings.image_provider.lower()

    if provider == "hf":
        return _generate_huggingface_image(
            prompt,
            output_path,
        )

    return _generate_local_image(
        prompt,
        output_path,
    )


def _generate_local_image(
    prompt: str,
    output_path: Path,
) -> str:

    pipeline = _get_local_pipeline()

    image = pipeline(
        prompt=prompt,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps,
        guidance_scale=settings.image_guidance,
    ).images[0]

    image.save(output_path)

    return f"/static/panels/{output_path.name}"


def _generate_huggingface_image(
    prompt: str,
    output_path: Path,
) -> str:

    if not settings.hf_api_key:
        raise RuntimeError(
            "HF_API_KEY is missing. Add it to .env."
        )

    url = (
        "https://api-inference.huggingface.co/models/"
        f"{settings.hf_image_model}"
    )

    headers = {
        "Authorization": f"Bearer {settings.hf_api_key}",
        "Accept": "image/png",
    }

    response = requests.post(
        url,
        headers=headers,
        json={"inputs": prompt},
        timeout=300,
    )

    response.raise_for_status()

    output_path.write_bytes(response.content)

    return f"/static/panels/{output_path.name}"