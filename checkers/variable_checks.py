import os
import httpx
from scripts.logger import get_logger
from scripts.load_configs import load_configs

logger = get_logger(__name__)
FB_PAGE_NAME = load_configs().get("your_page_name")

def write_to_summary(content: str) -> None:
    summary_file = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a") as f:
            f.write(content + "\n")

# Cabeçalho do relatório
write_to_summary('<h1 align="center">Verificação de Variáveis</h1>')
write_to_summary('<p align="center">Status das variáveis e tokens do sistema</p>')
write_to_summary('<div align="center">')
write_to_summary("\n| Variável | Status |")
write_to_summary("|----------|---------|")

def format_success(text: str) -> str:
    return f'<span style="color: #126329">✓ {text}</span>'

def format_error(text: str) -> str:
    return f'<span style="color: #82061E">⚠ {text}</span>'

def create_table_row(key: str, status: str) -> None:
    write_to_summary(f"| `{key}` | {status} |")

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

check_fb_token()
write_to_summary("\n</div>")
