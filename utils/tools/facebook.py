import httpx
from pathlib import Path
import os
from utils.tools.logger import get_logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError,
)

logger = get_logger(__name__)


class Facebook:
    def __init__(self, configs: dict, counter: dict):
        self.configs = configs
        self.counter = counter
        self.access_token = os.getenv("FB_TOKEN", "")
        self.api_version = configs.get("api_version", "v21.0")
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        self.client = httpx.Client(timeout=(10, 30))

        if not self.access_token:
            raise ValueError(
                "O token de acesso não foi encontrado \n"
                "nas variáveis de ambiente. Defina FB_TOKEN corretamente nas secrets do GitHub."
            )

    @retry(
        stop=stop_after_attempt(3),  # Máximo de 3 tentativas
        wait=wait_exponential(
            multiplier=1, min=2, max=10
        ),  # Tempo de espera exponencial
        retry=retry_if_exception_type(
            httpx.HTTPError
        ),  # Só tenta novamente se for erro HTTP
        reraise=True,  # Lança exceção se todas as tentativas falharem
    )
    def _try_post(self, endpoint: str, params: dict, files: dict = None) -> str | None:
        response = self.client.post(endpoint, params=params, files=files)

        if response.status_code == 200:
            try:
                return response.json().get("id")
            except ValueError:
                logger.error("Resposta não contém JSON válido")
                return None

        logger.error(f"Falha ao postar: {response.status_code} {response.text}")
        response.raise_for_status()  # Levanta exceção para ativar retry
        return None

    def post(
        self, message: str = "", frame_path: Path = None, parent_id: str = None
    ) -> str | None:
        """
        Posta uma mensagem no Facebook.
        Se todas as tentativas falharem, apenas loga o erro e retorna None.
        """
        endpoint = (
            f"{self.base_url}/{parent_id}/comments"
            if parent_id
            else f"{self.base_url}/me/photos"
        )
        params = {"access_token": self.access_token, "message": message}
        files = None

        if frame_path:
            with open(frame_path, "rb") as file:
                files = {"source": file}
                try:
                    return self._try_post(endpoint, params, files)
                except RetryError:
                    logger.error("Falha ao postar após múltiplas tentativas.")
                    return None
        else:
            try:
                return self._try_post(endpoint, params)
            except RetryError:
                logger.error("Falha ao postar após múltiplas tentativas.")
                return None

    def repost_to_album(
        self, message: str, frame_path: Path, configs: dict, counter: dict
    ) -> str | None:
        """
        Repost a frame to an album.
        Returns the post ID if successful, otherwise returns None.
        """
        album_id: str | int = (
            configs.get("episodes", {})
            .get(counter.get("current_episode", 0), {})
            .get("album_id", None)
        )

        if not album_id or not str(album_id).isdigit():
            return None

        print(
            f"├──Reposting frame in album_id: {album_id}...",
            flush=True,
        )
        return self.post(message, frame_path, parent_id=f"{album_id}/photos")

    def update_bio(self, message: str) -> str | None:
        endpoint = f"{self.base_url}/me/"
        data = {"access_token": self.access_token, "about": message}

        try:
            response = self.client.post(endpoint, data=data)
            if response.status_code != 200:
                logger.error(
                    f"Failed to update bio: {response.status_code} {response.text}"
                )
        except Exception as e:
            logger.error(f"Failed to update bio: {str(e)}", exc_info=True)

        print(
            f"\n\nBiography has been updated with message:\n{message}",
            flush=True,
        )
        return response.json().get("id")
