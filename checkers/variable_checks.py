import os

import httpx

from scripts.logger import get_logger
from scripts.load_configs import load_configs, load_frame_counter
from scripts.paths import frames_dir

logger = get_logger(__name__)

configs = load_configs()
frame_counter = load_frame_counter()

FB_PAGE_NAME = configs.get("your_page_name")
SUBTITLE = configs.get("posting").get("posting_subtitles")
EPISODE_NUMBER = frame_counter.get("current_episode")

SUMMARY_FILE = os.getenv("GITHUB_STEP_SUMMARY")

def write_to_summary(content: str) -> None:
    if SUMMARY_FILE:
        with open(SUMMARY_FILE, "a") as f:
            f.write(content + "\n")

# Cabeçalho do relatório
write_to_summary('<h1 align="center">Verificação de Variáveis</h1>')
write_to_summary('<p align="center">Status das variáveis e tokens do sistema</p>')
write_to_summary('<div align="center">')
write_to_summary("\n| Variável | Status |")
write_to_summary("|----------|---------|")


def format_success(text: str) -> str:
    return f"$\\fbox{{\\color{{#126329}}\\textsf{{✅  {text}}}}}$"  # LaTeX MathJax

def format_error(text: str) -> str:
    return f"$\\fbox{{\\color{{#82061E}}\\textsf{{❌  {text}}}}}$"   # LaTeX MathJax

def format_warning(text: str) -> str:
    return f"$\\fbox{{\\color{{#FFA500}}\\textsf{{⚠️  {text}}}}}$"  # LaTeX MathJax

def create_table_row(key: str, status: str) -> None:
    write_to_summary(f"| `{key}` | {status} |")



# Verificação do token do Facebook
def check_fb_token() -> None:
    fb_token = os.getenv("FB_TOKEN")
    if not fb_token:
        create_table_row("FB_TOKEN", format_error("Token não encontrado"))
        return
    
    try:
        response = httpx.get(
            "https://graph.facebook.com/me",
            params={"access_token": fb_token},
            timeout=15
        )
        response.raise_for_status()
        fb_page_name = response.json().get("name")

        if fb_page_name == FB_PAGE_NAME:
            create_table_row("FB_TOKEN", format_success("Token válido"))
        else:
            create_table_row("FB_TOKEN", format_error("Token inválido"))

    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP: {e}", exc_info=True)
        create_table_row("FB_TOKEN", format_error("Erro HTTP"))
    except Exception as e:
        logger.error(f"Erro inesperado: {e}", exc_info=True)
        create_table_row("FB_TOKEN", format_error("Erro inesperado"))
# Verificação do diretório de frames
def check_frames() -> None:
    episode_dir = frames_dir / f"{EPISODE_NUMBER:02}"
    
    if not episode_dir.exists():
        create_table_row("Frames", format_error("Diretório de frames não encontrado"))
        return
    
    frames_count = len(list(episode_dir.glob("*.jpg")))

    if frames_count == 0:
        create_table_row("Frames", format_error("Nenhum frame encontrado"))
        return

    create_table_row("Frames", format_success(f"{frames_count} frames encontrados"))

def check_subtitle() -> None:
    pass




check_fb_token()
check_frames()
check_subtitle()
write_to_summary("\n</div>")
