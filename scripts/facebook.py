import os
import time

import httpx
import asyncio

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

        response = httpx.post(endpoint, data=data, files=files, timeout=15)

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


# example:
#     # post image
#     post_id = fb_post(message="post title", frame_path="frame.jpg")


#     # add comment
#     comment_id = fb_post(message="subtitle", parent_id=post_id)
#     print(comment_id)


#     # random crop
#     random_crop = fb_post(message="random crop", frame_path="frameCrop.jpg", parent_id=post_id)
#     print(random_crop)


# ------------------------------------------------------------------------------------------------------------


# functions to repost images in album


def get_image_url(post_id, api_version="v21.0"):
    """
    Obtém a URL da imagem de um post.
    """
    try:
        url = f"https://graph.facebook.com/{api_version}/{post_id}"
        data = {"fields": "images", "access_token": os.getenv("FB_TOKEN")}

        response = httpx.get(url, params=data, timeout=15)
        response.raise_for_status()
        data = response.json()

        if "images" in data:
            return data["images"][0]["source"]

    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP ao obter URL da imagem: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao obter URL da imagem: {e}", exc_info=True)
        raise

def check_album_id(configs, frame_counter, fb_api_version) -> str:
        """
        check if album id is valid
        """
        ALBUM_ID = configs.get("episodes", {}).get(frame_counter.get("current_episode"), {}).get("album_id")
        ALBUM_ID = str(ALBUM_ID)

        if not ALBUM_ID or not ALBUM_ID.isdigit():
            logger.error("Your album id is invalid, check your configs", exc_info=True)
            return None

        try:
            response = httpx.get(
                f"https://graph.facebook.com/{fb_api_version}/{ALBUM_ID}/photos",
                params={"access_token": os.getenv("FB_TOKEN")},
                timeout=15,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Failed to find album. Status code: {response.status_code}, message: {response.text}",
                exc_info=True,
            )
            return None  # ou um valor padrão apropriado
        except Exception as e:
            logger.error(f"Unexpected error while finding album: {e}", exc_info=True)
            return None  # ou um valor padrão apropriado

        return ALBUM_ID


def repost_images_in_album(posts_data, configs, frame_counter):
    """
    Reposta imagens em um album.
    """
    fb_api_version = configs.get('fb_api_version', 'v21.0')

    # Use the new function in repost_images_in_album
    ALBUM_ID = check_album_id(configs, frame_counter, fb_api_version)
    if not ALBUM_ID:
        return None

    try:
        for post in posts_data:
            post_id = post.get("post_id")
            message = post.get("message")
            image_url = get_image_url(post_id)

            if all([post_id, message, image_url]):
                response = httpx.post(
                    f"https://graph.facebook.com/{fb_api_version}/{ALBUM_ID}/photos",
                    data={
                        "access_token": os.getenv("FB_TOKEN"),
                        "url": image_url,
                        "caption": message,
                    },
                    timeout=15,
                )

                if response.status_code != 200:
                    logger.error(
                        f"\tFalha ao postar no album. Status code: {response.status_code}, message: {response.text}",
                        exc_info=True,
                    )
                    return None  # ou um valor padrão apropriado
                else:
                    print("\n", "\tImage has been reposted", flush=True)

    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP ao repostar imagens: {e}", exc_info=True)
        return None  # ou um valor padrão apropriado
    except Exception as e:
        logger.error(f"Erro inesperado ao repostar imagens: {e}", exc_info=True)
        return None  # ou um valor padrão apropriado
