import sys
import config
from checkers import completed_episode, get_frame_interator_value





#main function
def main():
    if completed_episode == True:
        sys.exit(1) # the program will crash and close if the conditions are met

    
    frame_interator = get_frame_interator_value()

    for i in range(int(config.fph)):
        print((i+1) + frame_interator)
    

    

if __name__ == "__main__":
    main()


