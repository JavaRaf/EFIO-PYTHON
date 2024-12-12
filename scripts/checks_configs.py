import yaml
import os
import re

class CheckConfigs:

    def __init__(self):
        """
        Load the configuration file.
        """
        with open("Configs.yaml", "r") as ConfigsFile:
            self.configs: dict = yaml.safe_load(ConfigsFile)
    
    def get_config(self, key):
        """
        Retrieve a specific configuration by key.
        Args:
            key (str): The configuration key.
        Returns:
            any: The value associated with the key.
        """
        return self.configs.get(key)

    def episode_is_completed(self) -> bool:
        """
        Check if the current episode is complete.
        """

        if self.configs["episodes"][self.configs["current_episode"] - 1]["completed"] == True:
            print("Episode is complete!")
            return True
        else:
            return False

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
    check = CheckConfigs()  # Cria a instância da classe
    execution_interval = check.get_execution_interval()
    print(f"Execution interval: {execution_interval} hours")  # Imprime o intervalo de execução


