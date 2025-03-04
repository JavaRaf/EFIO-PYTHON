from email import message
import os
import time

import httpx

from scripts.load_configs import load_configs
from scripts.logger import get_logger

logger = get_logger(__name__)


def with_retries(max_attempts: int = 3, delay: float = 2.0):
    """
    Decorator para adicionar retries a uma função.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    logger.error(
                        f"Erro ao executar {func.__name__} (tentativa {attempt + 1}/{max_attempts}): {e}",
                        exc_info=True,
                    )
                    time.sleep(delay)

        return wrapper

    return decorator


@with_retries(max_attempts=3, delay=2.0)
def fb_update_bio(biography_text: str) -> None:
    """
    Atualiza a biografia da página do Facebook.
    """
    try:
        fb_api_version = load_configs().get("fb_api_version") or "v21.0"
        endpoint = f"https://graph.facebook.com/{fb_api_version}/me/"

        data = {"access_token": os.getenv("FB_TOKEN"), "about": biography_text}
        response = httpx.post(endpoint, data=data, timeout=15)
        if response.status_code != 200:
            logger.error(
                f"Falha ao atualizar a biografia. Status code: {response.status_code}, message: {response.text}",
                exc_info=True,
            )
            response.raise_for_status()

        print("\n", "Biography has been updated", flush=True)
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP ao atualizar a biografia: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar a biografia: {e}", exc_info=True)
        raise


@with_retries(max_attempts=3, delay=2.0)
def fb_posting(message: str, frame_path: str = None, parent_id: str = None) -> str:
    """
    Realiza postagens no Facebook com suporte a retry automático.

    Args:
        message (str): Mensagem/texto da postagem
        frame_path (str, opcional): Caminho para arquivo de imagem. Padrão None
        parent_id (str, opcional): ID do post pai para comentários. Padrão None

    Returns:
        str: ID da postagem/comentário criado

    Raises:
        Exception: Se todas as tentativas de postagem falharem
    """
    configs = load_configs()
    try:
        fb_api_version = configs.get("fb_api_version", "v21.0")

        endpoint = f"https://graph.facebook.com/{fb_api_version}/me/photos"

        if parent_id:
            endpoint = (
                f"https://graph.facebook.com/{fb_api_version}/{parent_id}/comments"
            )

        data = {"access_token": os.getenv("FB_TOKEN"), "message": message}

        files = {"source": open(frame_path, "rb")} if frame_path else None

        response = httpx.post(endpoint, data=data, files=files, timeout=30)

        if response.status_code != 200:
            logger.error(
                f"Falha ao postar. Status code: {response.status_code}, message: {response.text}",
                exc_info=True,
            )
            response.raise_for_status()

        return response.json()["id"]
    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP ao realizar postagem: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao realizar postagem: {e}", exc_info=True)
        raise


# usage example:
#     # post image
#     post_id = fb_post(message="post title", frame_path="frame.jpg")


#     # add comment
#     comment_id = fb_post(message="subtitle", parent_id=post_id)
#     print(comment_id)


#     # random crop
#     random_crop = fb_post(message="random crop", frame_path="frameCrop.jpg", parent_id=post_id)
#     print(random_crop)


# ------------------------------------------------------------------------------------------------------------


@with_retries(max_attempts=2, delay=2.0)
def check_album_id(configs, frame_counter, fb_api_version) -> tuple:
    """
    Verifica se o ID do álbum é válido.
    """
    ALBUM_ID = str(
        configs.get("episodes", {})
        .get(frame_counter.get("current_episode"), {})
        .get("album_id")
    )

    # um album id é valdio quando é um número inteiro presente no arquivo de configuração
    # Essa verificção não gera erros pois album_id pode esta preenchido com uma descrição do álbum
    if ALBUM_ID and not ALBUM_ID.isdigit():
        return None, None

    try:
        response = httpx.get(
            f"https://graph.facebook.com/{fb_api_version}/{ALBUM_ID}",
            params={"access_token": os.getenv("FB_TOKEN")},
            timeout=15,
        )
        response.raise_for_status()
        ALBUM_NAME = response.json().get("name")

    except httpx.HTTPStatusError:
        logger.error(
            f"Falha ao encontrar o álbum. Status code: {response.status_code}, message: {response.text}",
            exc_info=True,
        )
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao encontrar o álbum: {e}", exc_info=True)
        raise

    return ALBUM_ID, ALBUM_NAME


def repost_in_album(message: str, frame_path: str) -> None:
    """
    Reposte no álbum.

    Args:
        message (str): Mensagem a ser postada.
        frame_path (str): Caminho do frame.

    Returns:
        None
    """

    configs = load_configs()
    frame_counter = configs.get("frame_counter", {})
    fb_api_version = configs.get("fb_api_version", "v21.0")
    ALBUM_ID, ALBUM_NAME = check_album_id(configs, frame_counter, fb_api_version)

    if not ALBUM_ID or not ALBUM_NAME:
        return

    try:
        response = fb_posting(
            message,
            frame_path,
            parent_id=f"{ALBUM_ID}/photos"
        )

        if response.status_code != 200:
            logger.error(
                f"Falha ao repostar no álbum. Status code: {response.status_code}, message: {response.text}",
                exc_info=True,
            )
            response.raise_for_status()

        print(f"├── Reposted in album {ALBUM_NAME} (ID: {ALBUM_ID})")
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Falha ao repostar no álbum. Status code: {e.response.status_code}, message: {e.response.text}",
            exc_info=True,
        )
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao repostar no álbum: {e}", exc_info=True)
        raise