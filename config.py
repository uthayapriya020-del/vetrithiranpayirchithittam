from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    environment: str = "development"

    host: str = "127.0.0.1"
    port: int = 8000

    gemini_api_key: str = ""
    gemini_flash_model: str = "gemini-2.5-flash"
    gemini_pro_model: str = "gemini-2.5-pro"

    image_provider: str = "local"

    hf_api_key: str = ""
    hf_image_model: str = "runwayml/stable-diffusion-v1-5"

    local_image_model: str = "runwayml/stable-diffusion-v1-5"

    image_width: int = 768
    image_height: int = 512
    image_steps: int = 25
    image_guidance: float = 7.5

    panel_count: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def static_dir(self) -> Path:
        return BASE_DIR / "static"

    @property
    def panels_dir(self) -> Path:
        return self.static_dir / "panels"

    @property
    def exports_dir(self) -> Path:
        return self.static_dir / "exports"


settings = Settings()

settings.panels_dir.mkdir(parents=True, exist_ok=True)
settings.exports_dir.mkdir(parents=True, exist_ok=True)
