import yaml
import os
import re

class CheckConfigs_Class:

    def __init__(self):
        """
        Load the configuration file.
        """
        with open("Configs.yaml", "r") as ConfigsFile:
            self.configs: dict = yaml.safe_load(ConfigsFile)
    
    def get_yaml_values(self, key):
        if key not in self.configs:
            raise KeyError(f"The key '{key}' does not exist in the configuration.")
        return self.configs.get(key)

    
    def get_post_and_bio_message(self):
        """
        Get the post and bio variables from the message.
        Returns:
            dict: A dictionary containing all the variables to be used in the message and bio.
        """
        #   joins all variables into a dictionary to be used in the frame title or page biography
        message_variables = {
            "season": self.configs["season"],
            "episode": self.configs["episodes"][self.configs["current_episode"] - 1]["episode"],
            "total_frames": self.configs["episodes"][self.configs["current_episode"] - 1]["total_frames"],
            "fph": self.configs["episodes"][self.configs["current_episode"] - 1]["img_fps"],
            "page_name": self.configs["your_page_name"],
            "execution_interval": self.get_execution_interval()
        }

        return message_variables


    def episode_is_completed(self) -> bool:
        """
        Check if the current episode is complete.
        """
        if self.configs["episodes"][self.configs["current_episode"] - 1]["completed"] == True:
            print("Episode is complete!")
            return True
        else:
            return False

    def get_frame_path(self, frame_number: int) -> str:
        """
        Get the path to the frame image.
        Args:
            frame_number (int): The frame number.
        Returns:
            str: The path to the frame image.
        """
        current_episode = self.configs["current_episode"]
        frame_path = os.path.join("episodes", "frames", f"{current_episode:02d}", f"frame_{frame_number}.jpg")
        
        return frame_path


    def get_frame_iterator_value(self) -> int:
        """
        Get the frame interator value from the configuration file.
        Returns:
            int: The frame interator value.
        """
        return self.configs["episodes"][self.configs["current_episode"] - 1]["frame_interator"]
    
    # this function is weakly, but it works
    def get_execution_interval(self) -> int:
        """
        Get the execution interval value from the workflow file.
        Returns:
            int: The execution interval value.
        """
        with open(os.path.join(".github", "workflows", "first_process.yml"), "r") as workflow_file:
            workflow = workflow_file.readlines()

        for line in workflow:
            if line.replace(" ", "").startswith("-cron"):
                re.findall(r"\d+", line)
                return int(re.findall(r"\d+", line)[1])

    


# Exemplo de uso:
if __name__ == "__main__":
    check = CheckConfigs_Class()  # Cria a instância da classe

    print(check.get_frame_number(1))



