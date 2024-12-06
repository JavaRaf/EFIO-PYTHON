from parse_configs import parse_configs
from checkers import check_total_frames_posted


total_frames_posted: int = check_total_frames_posted()
configs: dict = parse_configs()


if total_frames_posted == int(configs["total_frame"]):
    print("All frames have been posted.")
else:
    print("Not all frames have been posted.")




