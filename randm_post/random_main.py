from time import sleep
import random
import os

from scripts.logger import get_logger
from randm_post.random_frame_path import get_random_episode_and_frame

logger = get_logger(__name__)



def random_main(fph, frame_counter, configs, frame_iterator, posting_interval):
    """Posta frames aleatórios"""

    for i in range(1, fph + 1):
        random_episode_number, random_frame_number = get_random_episode_and_frame()
