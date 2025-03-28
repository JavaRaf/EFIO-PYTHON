from PIL import Image, ImageEnhance
from pathlib import Path
import random
import os


# Constantes
OUTPUT_DIR = Path.cwd() / "utils" / "temp"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FRAMES_DIR = Path.cwd() / "frames"

def get_random_frame() -> tuple[Path, int, int]:
    """
    Returns:
        tuple[Path, int, int]: (caminho do arquivo, número do frame, número do episódio)
    """
    list_episodes = os.listdir(FRAMES_DIR)
    if not list_episodes:
        return None, None, None

    random_episode = random.choice(list_episodes)

    frames = [
        int(x.split("_")[1].split(".")[0])
        for x in os.listdir(f"{FRAMES_DIR}/{random_episode}")
        if x.startswith("frame_") and x.endswith(".jpg")
    ]
    if not frames:
        return None, None, None

    frame_number = random.choice(frames)
    frame_path = Path(FRAMES_DIR) / random_episode / f"frame_{frame_number}.jpg"
    return frame_path, frame_number, int(random_episode)

def None_filter(paths: list) -> Path:
    """Não aplica nenhum filtro, retornando a imagem original."""
    return paths[0]["frame_path"]

def two_panel(paths: list) -> Path:
    with Image.open(paths[0]["frame_path"]) as img1, Image.open(paths[1]["frame_path"]) as img2:
        image_width, image_height = img1.size
        img3 = Image.new("RGB", (image_width, image_height * 2))
        img3.paste(img1, (0, 0))
        img3.paste(img2, (0, image_height))

        output_path = OUTPUT_DIR / "_two_panel.jpg"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img3.save(output_path)
        return output_path

def mirror_image(paths: list) -> Path:
    """Espelha aleatoriamente o lado esquerdo ou direito da imagem."""
    with Image.open(paths[0]["frame_path"]) as img:
        width, height = img.size
        output_img = Image.new("RGB", (width, height))
        
        if random.choice([True, False]):
            half = img.crop((0, 0, width // 2, height))
            mirrored_half = half.transpose(Image.FLIP_LEFT_RIGHT)
            output_img.paste(half, (0, 0))
            output_img.paste(mirrored_half, (width // 2, 0))
        else:
            half = img.crop((width // 2, 0, width, height))
            mirrored_half = half.transpose(Image.FLIP_LEFT_RIGHT)
            output_img.paste(mirrored_half, (0, 0))
            output_img.paste(half, (width // 2, 0))

    output_path = OUTPUT_DIR / "_mirror_image.jpg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_img.save(output_path)
    return output_path

def brightness_and_contrast(paths: list, brightness: float = 0.8, contrast: float = 1.5) -> Path:
    """Aplica um filtro de brilho e contraste a uma imagem."""
    input_path = Path(paths[0]["frame_path"])
    output_path = OUTPUT_DIR / "_brightness_and_contrast.jpg"
    
    with Image.open(input_path) as img:
        img = ImageEnhance.Brightness(img).enhance(brightness)
        img = ImageEnhance.Contrast(img).enhance(contrast)
        img.save(output_path)
    
    return output_path

def negative_filter(paths: list) -> Path:
    """Aplica um filtro negativo."""
    with Image.open(paths[0]["frame_path"]) as img:
        output_img = img.convert("RGB").point(lambda x: 255 - x)
    
    output_path = OUTPUT_DIR / "_negative_filter.jpg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_img.save(output_path)
    
    return output_path

def warp_in(paths: list) -> Path:
    with Image.open(paths[0]["frame_path"]) as img:
        output_img = img.convert("RGB")
    
    output_path = OUTPUT_DIR / "_warp_in.jpg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_img.save(output_path)
    
    return output_path

def warp_out(paths: list) -> Path:
    with Image.open(paths[0]["frame_path"]) as img:
        output_img = img.convert("RGB")
    
    output_path = OUTPUT_DIR / "_warp_out.jpg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_img.save(output_path)
    
    return output_path
