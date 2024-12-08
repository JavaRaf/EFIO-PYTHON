import sys
from checkers import check_total_frames_are_posted
from checkers import logging



#main function
def main():
    if check_total_frames_are_posted() == True:
        sys.exit(1) # the program will crash and close if the conditions are met

    
    # loop para postar a quatidade de frames escolhida o config.conf




if __name__ == "__main__":
    main()


