from pathlib import Path

from fastapi import (
    APIRouter,
    Form,
    Request,
)
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
)
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR, settings
from app.schemas import PromptRequest

from app.services.gemini import (
    generate_outline,
    generate_story,
)

from app.services.image_generator import (
    generate_image,
)

from app.services.layout_builder import (
    build_comic_layout,
)

from app.services.exporters import (
    save_pdf,
)


router = APIRouter()

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


@router.get(
    "/",
    response_class=HTMLResponse,
)
async def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        },
    )


async def generate_comic(
    data: PromptRequest,
):

    # Step 1: Generate comic outline
    outline = generate_outline(
        story_prompt=data.story_prompt,
        character_name=data.character_name,
        setting=data.setting,
        tone=data.tone,
        art_style=data.art_style,
    )

    # Step 2: Generate detailed story
    story = generate_story(
        outline=outline,
        character_name=data.character_name,
        tone=data.tone,
    )

    # Step 3: Generate images
    image_paths = []

    for panel in story.get("panels", []):

        prompt = panel.get(
            "image_prompt",
            "",
        )

        image_path = generate_image(
            prompt=prompt,
            filename_prefix=f"panel_{panel.get('panel_number', 1)}",
        )

        image_paths.append(image_path)

    # Step 4: Build layout
    comic = build_comic_layout(
        story_data=story,
        image_paths=image_paths,
    )

    # Step 5: Export PDF
    pdf_url = save_pdf(comic)

    comic["pdf_url"] = pdf_url

    return comic


@router.post(
    "/generate",
    response_class=HTMLResponse,
)
async def generate_from_form(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form("Alex"),
    setting: str = Form("A futuristic city"),
    tone: str = Form("Adventure"),
    art_style: str = Form("Comic book"),
):

    try:

        data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        comic = await generate_comic(data)

        return templates.TemplateResponse(
            "comic_preview.html",
            {
                "request": request,
                "comic": comic,
            },
        )

    except Exception as exc:

        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": str(exc),
            },
            status_code=500,
        )


@router.post("/generate-comic/json")
async def generate_comic_json(
    data: PromptRequest,
):

    try:

        comic = await generate_comic(data)

        return JSONResponse(
            content=comic
        )

    except Exception as exc:

        return JSONResponse(
            status_code=500,
            content={
                "error": str(exc)
            },
        )


@router.post("/test-image")
async def test_image():

    try:

        image = generate_image(
            prompt=(
                "A colorful comic book hero "
                "standing in a futuristic city, "
                "dynamic lighting, detailed illustration"
            ),
            filename_prefix="test",
        )

        return {
            "success": True,
            "image": image,
        }

    except Exception as exc:

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(exc),
            },
        )


@router.get(
    "/download-success",
    response_class=HTMLResponse,
)
async def download_success(
    request: Request,
):

    return templates.TemplateResponse(
        "export_success.html",
        {
            "request": request,
        },
    )


@router.get(
    "/export-success",
    response_class=HTMLResponse,
)
async def export_success(
    request: Request,
):

    return templates.TemplateResponse(
        "export_success.html",
        {
            "request": request,
        },
    )