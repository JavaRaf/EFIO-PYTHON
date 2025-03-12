from email import message
import os
import time

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


from scripts.load_configs import load_configs, load_frame_counter
from scripts.logger import get_logger

logger = get_logger(__name__)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10))
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


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10))
def check_if_post_exists(message: str, posts: list) -> str:
    """
    Verifica se o post já existe em uma lista de posts.
    """
    for post in posts:
        if post["message"] == message:
            return post["id"]
    return None

# contador de falhas, evitar posts repetidos por causa dos timeouts
static_fails = 0

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10))
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
    global static_fails
    configs = load_configs()

    if static_fails > 0:
        # recupera os 10 posts mais recentes
        endpoint = f"https://graph.facebook.com/{configs.get('fb_api_version', 'v21.0')}/me/posts"
        params = {"access_token": os.getenv("FB_TOKEN"), "limit": 10}
        response = httpx.get(endpoint, params=params, timeout=20)
        response.raise_for_status()
        posts = response.json().get("data", [])

        post_id = check_if_post_exists(message, posts)
        if post_id:
            return post_id

    
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
            static_fails += 1
            response.raise_for_status()
            

        return response.json()["id"]
    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP ao realizar postagem: {e}", exc_info=True)
        static_fails += 1
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao realizar postagem: {e}", exc_info=True)
        static_fails += 1
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


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=2, min=2, max=10))
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
    if not ALBUM_ID or not ALBUM_ID.isdigit():
        print("Album ID inválido, as imagens não serão repostadas no álbum", flush=True)
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

# não tem retry, pq usar a função de postagem acima
def repost_in_album(post_data: dict) -> None:
    """
    Reposte no álbum.

    Args:
        post_data (dict): Dicionário com dados de postagem.
        frame_path (str): Caminho do frame.

    Returns:
        None
    """

    configs = load_configs()
    frame_counter = load_frame_counter()
    fb_api_version = configs.get("fb_api_version", "v21.0")
    ALBUM_ID, ALBUM_NAME = check_album_id(configs, frame_counter, fb_api_version)

    if not ALBUM_ID or not ALBUM_NAME:
        logger.error(
            f"Falha ao encontrar o álbum. ID: {ALBUM_ID}, Nome: {ALBUM_NAME}",
            exc_info=True,
        )
        return

    for post in post_data:
        try:
            fb_posting(
                post["message"], post["frame_path"], parent_id=f"{ALBUM_ID}/photos"
            )
        except Exception as e:
            logger.error(f"Erro inesperado ao repostar no álbum: {e}", exc_info=True)
            raise

        print(
            f"├── Episode {post['episode_number']} Frame {post['frame_number']} Reposted in album ({ALBUM_NAME}) (ID: {ALBUM_ID})"
        )

        time.sleep(2)
