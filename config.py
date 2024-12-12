# Imports | Don't change imports unless you know
import os

# ------------------------------------------ bots settings ------------------------------------------------#

EFIO           = True       # Every frame in order. Basic bot that posts all frames in sequence
frame_download = False      # If true, allows the download of posted frames by commands
Random_post    = False      # If true, allows the random posting of frames
                            # Be careful when activating more than one bot at a time

# ------------------------------------------ Basic settings ------------------------------------------------#

# You can find these settings in the episodes folder. File name is Configs.jsonc

# "season": 1,              # Season number of the episode
# "episode": 1,             # Episode number of the episode
# "total_frames": 4000,     # Total frames of the episode cutted
# "img_fps": 3.5,           # value used to crop the frames
# "frame_interator": 1,     # Number of frames posted in the current episode
# "fb_frames_album": "",    # id of the album where the frames will be posted on facebook
# "your_page_name": "",     # name of your facebook frames page

# "completed": false        # True if the episode is completed, the bot does not post completed episodes


# ------------------------------------------- secondary settings ---------------------------------------------#

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
#    Message to be posted in the page bio of your facebook page
#    available variables are:
#    {season}               (shows the current season)
#    {episode}              (shows the current episode)
#    {img_fps}              (image frames per second)
#    {fph}                  (number of frames posted in the execution interval)
#    {execution_interval}   (execution interval)
#    {total_frames_posted}  (total number of frames posted)

# ---------------------------------- Posting Subtitles Variables --------------------------------------------#
                            
posting_subtitles       = True  # If true, make a comment on the post with the subtitle referring to the posted frame
random_crop             = True  # If true, make a random cut of the frame and post it in the comments
fph                     = 15    # Number of frames posted in the execution interval
sub_posting_interval    = 2     # Interval between each frame (in minutes), (Default is 2)
delay_action            = 3     # Delay of the Each action (in seconds), (Default is 3)


rcrop_x = 200 # x-coordinate of the random crop
rcrop_y = 600 # y-coordinate of the random crop
# The value must be smaller than the resolution of your frame


# ---------------------------------- Environment variables -----------------------------------------------#

FB_API_VERSION = "v21.0"         # Facebook API version ( changing in case of deprecation )
FB_URL = f"https://graph.facebook.com/{FB_API_VERSION}/" # Facebook API URL
FB_TOKEN = os.getenv("FB_TOKEN") # Facebook access token ( present in actions secrets )

