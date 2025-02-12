from pathlib import Path

# dirs paths
episodes_dir = Path(__file__).parent.parent / "episodes"
frames_dir = episodes_dir / "frames"
subtitles_dir = episodes_dir / "subtitles"

# files paths
frame_counter_path = Path(__file__).parent.parent / "frame_counter.yaml"
configs_path = Path(__file__).parent.parent / "configs.yaml"
fb_log_path = Path(__file__).parent.parent / "fb" / "fb_log.txt"
