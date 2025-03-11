from PIL import Image
from pathlib import Path
import random


def two_panel(paths: list) -> Path:
    with Image.open(paths[0]["frame_path"]) as img1, Image.open(
        paths[1]["frame_path"]
    ) as img2:
        image_width, image_height = img1.size

        img3 = Image.new("RGB", (image_width, image_height * 2))
        img3.paste(img1, (0, 0))
        img3.paste(img2, (0, image_height))

        output_path = Path("episodes/filtereds_frames") / f"_two_panel.jpg"
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        img3.save(output_path)

        return output_path


def mirror_image(paths: list) -> Path:
    """
    Espelha aleatoriamente o lado esquerdo ou direito da imagem.
    """
    width, height = Image.open(paths[0]["frame_path"]).size

    with Image.open(paths[0]["frame_path"]) as img:
        output_img = Image.new("RGB", (width, height))
        
        if random.choice([True, False]):  # Escolhe aleatoriamente qual lado espelhar
            # Espelhar o lado esquerdo
            half = img.crop((0, 0, width // 2, height))
            mirrored_half = half.transpose(Image.FLIP_LEFT_RIGHT)
            output_img.paste(half, (0, 0))
            output_img.paste(mirrored_half, (width // 2, 0))
        else:
            # Espelhar o lado direito
            half = img.crop((width // 2, 0, width, height))
            mirrored_half = half.transpose(Image.FLIP_LEFT_RIGHT)
            output_img.paste(mirrored_half, (0, 0))
            output_img.paste(half, (width // 2, 0))
    
    output_path = Path("episodes/filtereds_frames") / "_mirror_image.jpg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_img.save(output_path)

    return output_path



def negative_filter(paths: list) -> Path:
    """Aplica um filtro negativo"""
    with Image.open(paths[0]["frame_path"]) as img:
        output_img = img.convert("RGB").point(lambda x: 255 - x)

    output_path = Path("episodes/filtereds_frames") / f"_negative_filter.jpg"
    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_img.save(output_path)

    return output_path


def generate_palette(paths: list) -> Path:
    pass


def warp_in(paths: list) -> Path:
    pass


def warp_out(paths: list) -> Path:
    pass
