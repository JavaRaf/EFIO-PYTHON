import httpx
import config



def post_frame_on_fb(image_path: str, frame_number: int) -> str:
 
    with open(image_path, 'rb') as image:
        frame = {"source": image}

        data = {
        "access_token": config.FB_TOKEN,
        "message": config.post_message.format(),
        }
    
        response = httpx.post(f"{config.FB_URL}/me/photos", data=data, files=frame, timeout=10)

    if response.status_code == 200:
        print(f"Successfully posted frame with id {response.json()['id']}")
        return response.json()['id']
    else:
        print(f"Failed to post frame. Status code: {response.status_code}")


