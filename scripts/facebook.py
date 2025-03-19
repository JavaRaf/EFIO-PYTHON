import os
import time

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from scripts.load_configs import load_configs, load_frame_counter
from scripts.logger import get_logger

logger = get_logger(__name__)
client = httpx.Client(timeout=(10, 30))


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10),
    retry=retry_if_exception_type(
        (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError)
    ),
)
def fb_update_bio(biography_text: str) -> None:
    """
    Updates the Facebook page biography.
    """
    try:
        fb_api_version = load_configs().get("fb_api_version") or "v21.0"
        endpoint = f"https://graph.facebook.com/{fb_api_version}/me/"

        data = {"access_token": os.getenv("FB_TOKEN"), "about": biography_text}
        response = httpx.post(endpoint, data=data, timeout=15)
        if response.status_code != 200:
            logger.error(
                f"Failed to update biography. Status code: {response.status_code}, message: {response.text}",
                exc_info=True,
            )
            response.raise_for_status()

        print(
            f"\n\nBiography has been updated with message:\n\t {biography_text}",
            flush=True,
        )
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while updating biography: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error while updating biography: {e}", exc_info=True)
        raise


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10),
    retry=retry_if_exception_type(
        (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError)
    ),
)
def fb_posting(message: str, frame_path: str = None, parent_id: str = None) -> str:
    configs = load_configs()
    fb_api_version = configs.get("fb_api_version", "v21.0")

    endpoint = f"https://graph.facebook.com/{fb_api_version}/me/photos"
    if parent_id:
        endpoint = f"https://graph.facebook.com/{fb_api_version}/{parent_id}/comments"

    data = {"access_token": os.getenv("FB_TOKEN"), "message": message}
    files = None

    try:
        if frame_path:
            with open(frame_path, "rb") as file:
                files = {"source": file}
                response = client.post(endpoint, data=data, files=files)
        else:
            response = client.post(endpoint, data=data)

        response.raise_for_status()  # Raises error for bad HTTP status codes (400+)

        return response.json().get("id")

    except httpx.HTTPStatusError as e:
        logger.error(
            f"HTTP Error: {e.response.status_code} - {e.response.reason_phrase}"
        )
        if e.response.status_code >= 400 and e.response.status_code < 500:
            raise  # 4xx errors usually shouldn't be retried

    except httpx.TimeoutException as e:
        logger.error(f"Timeout while posting: {e}")
        raise

    except httpx.NetworkError as e:
        logger.error(f"Network error: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error while posting: {e}", exc_info=True)
        raise


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=2, min=2, max=10))
def check_album_id(configs, frame_counter, fb_api_version) -> tuple:
    """
    Checks if the album ID is valid.
    """
    ALBUM_ID = str(
        configs.get("episodes", {})
        .get(frame_counter.get("current_episode"), {})
        .get("album_id")
    )

    # An album ID is valid when it's an integer number present in the configuration file
    if not ALBUM_ID or not ALBUM_ID.isdigit():
        print("Invalid Album ID, images will not be reposted in the album", flush=True)
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
            f"Failed to find album. Status code: {response.status_code}, message: {response.text}",
            exc_info=True,
        )
        raise
    except Exception as e:
        logger.error(f"Unexpected error while finding album: {e}", exc_info=True)
        raise

    return ALBUM_ID, ALBUM_NAME


# No retry because it uses the posting function above
def repost_in_album(post_data: dict) -> None:
    """
    Reposts in the album.

    Args:
        post_data (dict): Dictionary with posting data.

    Returns:
        None
    """

    configs = load_configs()
    frame_counter = load_frame_counter()
    fb_api_version = configs.get("fb_api_version", "v21.0")
    ALBUM_ID, ALBUM_NAME = check_album_id(configs, frame_counter, fb_api_version)

    if not ALBUM_ID or not ALBUM_NAME:
        logger.error(
            f"Failed to find album. ID: {ALBUM_ID}, Name: {ALBUM_NAME}",
            exc_info=True,
        )
        return

    print("\nReposting frames in album...\n")
    for post in post_data:
        try:
            fb_posting(
                post["message"], post["frame_path"], parent_id=f"{ALBUM_ID}/photos"
            )
        except Exception as e:
            logger.error(
                f"Unexpected error while reposting in album: {e}", exc_info=True
            )
            raise

        print(
            f"├── Episode {post['episode_number']} Frame {post['frame_number']} Reposted in album ({ALBUM_NAME}) (ID: {ALBUM_ID})"
        )

        time.sleep(2)
