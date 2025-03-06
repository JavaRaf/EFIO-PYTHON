from random_post.random_frame import get_random_frame
from PIL import Image
from pathlib import Path


def two_panel_base(frame_path: Path) -> Path:
    frame_path2, _, _ = get_random_frame()
    
    with Image.open(frame_path) as img1, Image.open(frame_path2) as img2:
        image_width, image_height = img1.size
        
        img3 = Image.new('RGB', (image_width, image_height*2))
        img3.paste(img1, (0, 0))
        img3.paste(img2, (0, image_height))
        
        output_path = Path("episodes/filtereds_frames") / f"_two_panel.jpg"
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        img3.save(output_path)
        
        return output_path

def mirror_image_base(frame_path: Path) -> Path:
    pass

def negative_filter_base(frame_path: Path) -> Path:
    pass

def generate_palette_base(frame_path: Path) -> Path:
    pass

def warp_in_base(frame_path: Path) -> Path:
    pass

def warp_out_base(frame_path: Path) -> Path:
    pass




