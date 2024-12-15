import sys
import time
from scripts import CheckConfigs_Class, FacebookFunctions_Class


configs  = CheckConfigs_Class() 
fb      = FacebookFunctions_Class()


# main function
def main():
    if configs.episode_is_completed() == True:
        sys.exit(1) # the program will crash and close if the conditions are met


    for i in range(1, configs.get_yaml_values("fph") + 1):

        # get the frame number
        frame_number = i + configs.get_frame_iterator_value()
        # get the path to the frame image
        frame_path = configs.get_frame_path(frame_number)
        # post the frame to facebook
        fb.post_frame(frame_path, frame_number)
        # wait 10 second between frames to avoid hitting the rate limit
        time.sleep(10)  
        
         

if __name__ == "__main__":
    main()


