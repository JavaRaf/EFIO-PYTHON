import sys
from scripts.checks_configs import CheckConfigs


checks = CheckConfigs()



# main function
def main():
    if checks.episode_is_completed() == True:
        sys.exit(1) # the program will crash and close if the conditions are met



    
    for i in range(1, checks.get_config("fph") + 1):
        print(i + checks.get_frame_iterator_value())
        
         

if __name__ == "__main__":
    main()


