import logging
import config
import re




def total_frames_posted() -> int:
    """
    This function checks the total number of frames posted by the bot.
    Returns the total number of frames posted.
    """

    with open("total_frames_posted.txt", "r", encoding="utf-8") as file_counter_total_frames:
        counter_total_frames = file_counter_total_frames.readlines()
       
        for line in counter_total_frames:
            if line.startswith("total_frames_posted"):
                number_total_frames_posted = int(line.replace(" ", "").split("=")[1])

                return number_total_frames_posted
        
            

def check_total_frames_are_posted():
    """
    Checks if all the frames were posted.
    Returns True if all the frames were posted, False otherwise.
    """
    all_posted: bool = total_frames_posted() == int(config.total_frames)

    if all_posted == True:
        print (message := "All frames were posted")
        logging.info(message)  # log the message

    return all_posted



# # this function is weak, and may fail in more detailed crons
def get_execution_interval() -> int:
    """
    This function checks the execution interval of the bot.
    Returns the execution interval of the bot.
    """

    with open(".github/workflows/first_process.yml", "r", encoding="utf-8") as file_first_process:
        first_process = file_first_process.readlines()
        for line in first_process:
            if line.replace(" ", "").startswith("-cron:") and not line.replace(" ", "").startswith("#"):
                execution_interval = re.findall("\d+", line)[1]

                return int(execution_interval)

                


                        
                    
                

                




                


get_execution_interval()

                

# configure logging settings
logging.basicConfig(
    filename="system_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


        
