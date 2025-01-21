import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()


@dataclass
class Config:
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1")
    # Do not set HEADFUL_BROWSER to true in containers
    HEADFUL_BROWSER = os.getenv("HEADFUL_BROWSER", "False").lower() in ("true", "1")

    CHROME_DRIVER_PATH = ChromeDriverManager().install()
    TEMPLATE_PATH = Path("src/templates.yaml")
    CSS_PATH = Path("src/style.css")

    EMAIL = ""
    PASSWORD = ""

    GOOGLE_API_KEY = ""


class DevelopmentConfig(Config):
    DEBUG = True
    EMAIL = os.getenv("EMAIL", "")
    PASSWORD = os.getenv("PASSWORD", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")


class ProductionConfig(Config):
    DEBUG = False


is_debug = os.getenv("DEBUG", "False").lower() in ("true", "1")

settings: Config

if is_debug:
    settings = DevelopmentConfig()
else:
    settings = ProductionConfig()
