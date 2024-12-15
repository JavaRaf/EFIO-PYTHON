import httpx
import os
from .CheckConfigs import CheckConfigs_Class

configs = CheckConfigs_Class()


class FacebookFunctions_Class:

    def __init__(self):
        self.FB_TOKEN = os.getenv("FB_TOKEN")
        self.FB_URL = configs.get_yaml_values("FB_URL")
        self.FB_API_VERSION = configs.get_yaml_values("FB_API_VERSION")


    def post_frame(self, frame_path: str, frame_number: int) -> str:
        """
        Post a frame(image) to Facebook.

        Args:
            frame_path (str): The path to the frame image.
            frame_number (int): The frame number.
        Returns:
            str: The ID of the posted frame.
        """
        # joins all variables into a dictionary to be used in the frame title or page biography
        message_variables = {**configs.get_post_and_bio_message(), "current_frame": frame_number}

        try:
            with open(frame_path, 'rb') as frame_file:
                frame = {"source": frame_file}

                data = {
                "access_token": self.FB_TOKEN,
                "message": configs.get_yaml_values("post_message").format(**message_variables)
                    
                }
            
                response = httpx.post(f"{self.FB_URL}/{self.FB_API_VERSION}/me/photos", data=data, files=frame, timeout=10)

            if response.status_code == 200:
                print(f"Successfully posted frame with id {response.json()['id']}")
                return response.json()['id']
            else:
                print(f"Failed to post frame. Status code: {response.status_code}")
        
        except Exception as e:
            print(f"Failed to post frame. Error: {e}")


