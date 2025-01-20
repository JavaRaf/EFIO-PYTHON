import time
import httpx
import os




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
                    print(f"Tentativa {attempt + 1} falhou. Erro: {e}")
                    time.sleep(delay)
        return wrapper
    return decorator


@with_retries(max_attempts=3, delay=2.0)
def fb_update_bio(biography_text: str, config: dict) -> None:
    """
    Atualiza a biografia da página do Facebook.
    """
    endpoint = f"https://graph.facebook.com/{config.get("fb_api_version")}/me/"
    data = {
        "access_token": os.getenv("TOK_FB"),
        "about": biography_text
    }
    response = httpx.post(endpoint, data=data, timeout=15)
    if response.status_code != 200:
        raise Exception(f"Falha ao atualizar a biografia. Status code: {response.status_code}")
    
    print("updated bio", flush=True)
    return response.json()


@with_retries(max_attempts=3, delay=2.0)
def fb_post(message: str, frame_path: str = None, parent_id: str = None, config: dict = None) -> str:
    """
    Realiza postagens no Facebook com suporte a retry automático.

    Args:
        endpoint (str): Endpoint da API do Facebook (ex: "photos", "feed")
        message (str): Mensagem/texto da postagem
        frame_path (str, opcional): Caminho para arquivo de imagem. Padrão None
        parent_id (str, opcional): ID do post pai para comentários. Padrão None
        fb_api_version (str, opcional): Versão da API do Facebook. Padrão "v21.0"

    Returns:
        str: ID da postagem/comentário criado

    Raises:
        Exception: Se todas as tentativas de postagem falharem
    """
    fb_api_version = config.get("fb_api_version") or "v21.0"
    endpoint = "photos"
    # Construir o endpoint base
    if parent_id:
        # Para comentários em posts existentes
        endpoint = f"https://graph.facebook.com/{fb_api_version}/{parent_id}/comments"
    else:
        # Para novos posts
        endpoint = f"https://graph.facebook.com/{fb_api_version}/me/{endpoint}"
    
    data = {
        "access_token": os.getenv("TOK_FB"),
        "message": message
    }

    files = {"source": open(frame_path, 'rb')} if frame_path else None

    response = httpx.post(endpoint, data=data, files=files, timeout=15)

    if response.status_code != 200:
        raise Exception(f"Falha ao fazer post. Status code: {response.status_code}, message: {response.text}")
    
    return response.json()["id"]


# Exemplo de uso:
# try:
#     # Postar imagem
#     post_id = fb_post(endpoint="photos", message="post title", frame_path="frame.gif")
#     # Adicionar comentário
#     comment_id = fb_post(endpoint="photos", message="subtitle", parent_id=post_id)
#     # Adicionar random crop
#     rand_crop = fb_post(endpoint="photos", message="random crop", parent_id=post_id, frame_path="frame.gif")
#     print(comment_id)
# except Exception as e:
#     print(f"Todas as tentativas falharam. Erro final: {e}")



    