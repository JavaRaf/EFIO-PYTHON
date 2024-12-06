




def check_total_frames_posted() -> int:

    """
    This function checks the total number of frames posted by the bot.
    Returns the total number of frames posted.
    """

    with open("counter_total_frames.txt", "r", encoding="utf-8") as file_counter_total_frames:
        counter_total_frames = file_counter_total_frames.readlines()
       
        for line in counter_total_frames:
            if line.startswith("counter_total_frames"):
                number_total_frames_posted = int(line.replace(" ", "").split("=")[1])

                return number_total_frames_posted
        
                


