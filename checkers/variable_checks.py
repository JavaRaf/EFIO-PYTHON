import os
import httpx

from scripts.logger import get_logger
from scripts.load_configs import load_configs

logger = get_logger(__name__)
FB_PAGE_NAME = load_configs().get("your_page_name")

# Função para escrever no GITHUB_STEP_SUMMARY
def write_to_summary(content: str) -> None:
    summary_file = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a") as f:
            f.write(content + "\n")

# Cabeçalho da tabela
write_to_summary("\n| Variable | Value |")
write_to_summary("|----------|-------|")

def create_table(key: str, value: str, color: str) -> None:
    if color == "red":
        write_to_summary(f"|{key} | <span style='color:red'>{value}</span>|")
    elif color == "green":
        write_to_summary(f"|{key} | <span style='color:green'>{value}</span>|")

def check_fb_token() -> None:
    """
    Verifica se o token do Facebook está válido.
    """
    fb_token = os.getenv("FB_TOKEN")
    if not fb_token:
        create_table("FB_TOKEN", "secret not found", "red")
        return
    
    try:
        response = httpx.get(
            "https://graph.facebook.com/me",
            params={"access_token": fb_token}, timeout=15
        )
        response.raise_for_status()
        fb_page_name = response.json().get("name")

        if fb_page_name == FB_PAGE_NAME:
            create_table("FB_TOKEN", "fb token is valid", "green")
        else:
            create_table("FB_TOKEN", "fb token is invalid", "red")

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while verifying Facebook token: {e}", exc_info=True)
        create_table("FB_TOKEN", "HTTP error occurred", "red")
    except Exception as e:
        logger.error(f"Unexpected error while verifying Facebook token: {e}", exc_info=True)
        create_table("FB_TOKEN", "unexpected error occurred", "red")

# Chama a função para verificar o token do Facebook
check_fb_token()
