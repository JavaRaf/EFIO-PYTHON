# Imports | Don't change imports unless you know
import os


# ---------------------------------- Fill the Required Variables --------------------------------------------# 

season  = "1"
episode = "01"
total_frames = "4000"
img_fps = ""
page_name = ""

# ----------------------------------------------------------------------------------------------------------#

post_message = "Season {season}, Episode {episode}, Frame {current_frame} out of {total_frame}"
#    available variables are:
#    {season}           (shows the current season)
#    {episode}          (shows the current episode)
#    {total_frames}     (shows the total frame)
#    {frame_timestamp}  (approximate timestamp of current frame)
#    {fph}              (number of frames posted in the execution interval)
#    {page_name}        (name of your  facebook page)
#    \n                 (new-line character) 

# ----------------------------------------------------------------------------------------------------------#


page_bio = (
    "Chopped {img_fps} FPS, Posting {fph} Frames every\n"
    "{execution_interval} hours. Total of '{total_frames_posted}' frame was successfully posted!!"
)
# Message to be posted in the page bio of your facebook page
#    available variables are:
#    {season}               (shows the current season)
#    {episode}              (shows the current episode)
#    {img_fps}              (image frames per second)
#    {fph}                  (number of frames posted in the execution interval)
#    {execution_interval}   (execution interval)
#    {total_frames_posted}  (total number of frames posted)

# ---------------------------------- Posting Subtitles Variables --------------------------------------------#
             
posting_subtitles = "1"     # If active, make a comment on the post with the caption referring to the posted frame
random_crop = "1"           # If active, make a random cut of the frame and post it in the comments
fb_frames_album = ""        # ID of the album where the frames will be uploaded
fph = "15"                  # Number of frames posted in the execution interval
delay_action = "3"          # Delay of the Each action (in seconds), (Default is 3
sub_posting_interval = "2"  # Interval between each frame (in minutes), (Default is 2)


rcrop_x = "200" # x-coordinate of the random crop
rcrop_y = "600" # y-coordinate of the random crop
# The value must be smaller than the resolution of your frame


# ---------------------------------- Environment variables -----------------------------------------------#

FB_API_VERSION = "v21.0" # Facebook API version ( changing in case of deprecation )
FB_TOKEN = os.getenv("FB_TOKEN") # Facebook access token ( present in actions secrets )

