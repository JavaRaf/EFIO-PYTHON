from CheckConfigs import CheckConfigs_Class
import os



configs = CheckConfigs_Class()


class Subtitles:
    def __init__(self):
        pass
    
    def get_subtitles(self, frame_number: int):
        """
        Get the subtitle(s) for a given frame number.

        Args:
            frame_number (int): The frame number.
            Returns:
                str: The subtitle(s) for the given frame number.
        """

        episodes = configs.get_yaml_values("episodes")
        current_episode = configs.get_yaml_values("current_episode")
        img_fps = episodes[current_episode - 1]["img_fps"]

        total_seconds = frame_number / img_fps

        minutes = int(total_seconds // 60)  
        seconds = int(total_seconds % 60)  
        milliseconds = int((total_seconds - int(total_seconds)) * 100) 

        time_str = f"{minutes:02d}:{seconds:02d}:{milliseconds:02d}"

        print(time_str)
        

subtitles = Subtitles()
subtitles.get_subtitles(10)



