from PIL import Image, ImageEnhance
from pathlib import Path
import random
from scripts.paths import filtereds_frames_dir


def None_filter(paths: list) -> Path:
    """Não aplica nenhum filtro, retornando a imagem original."""
    return paths[0]["frame_path"]

def two_panel(paths: list) -> Path:
    with Image.open(paths[0]["frame_path"]) as img1, Image.open(
        paths[1]["frame_path"]
    ) as img2:
        image_width, image_height = img1.size

        img3 = Image.new("RGB", (image_width, image_height * 2))
        img3.paste(img1, (0, 0))
        img3.paste(img2, (0, image_height))

        output_path = filtereds_frames_dir / f"_two_panel.jpg"
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
    
    output_path = filtereds_frames_dir / "_mirror_image.jpg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_img.save(output_path)

    return output_path


def brightness_and_contrast(paths: list, brightness: float = 0.8, contrast: float = 1.5) -> Path:
    """Aplica um filtro de brilho e contraste a uma imagem."""
    
    input_path = Path(paths[0]["frame_path"])
    output_path = filtereds_frames_dir / f"_brightness_and_contrast.jpg"
    
    with Image.open(input_path) as img:
        # Aplica brilho
        img = ImageEnhance.Brightness(img).enhance(brightness)
        # Aplica contraste
        img = ImageEnhance.Contrast(img).enhance(contrast)
        # Salva a imagem processada
        img.save(output_path)

    return output_path


def negative_filter(paths: list) -> Path:
    """Aplica um filtro negativo"""
    with Image.open(paths[0]["frame_path"]) as img:
        output_img = img.convert("RGB").point(lambda x: 255 - x)

    output_path = filtereds_frames_dir / f"_negative_filter.jpg"
    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_img.save(output_path)

    return output_path


def generate_palette(paths: list[dict]) -> Path:
    """Gera uma paleta de cores e salva no formato JPEG."""
    pass
        

def warp_in(paths: list) -> Path:
    with Image.open(paths[0]["frame_path"]) as img:
        output_img = img.convert("RGB")

    output_path = filtereds_frames_dir / f"_warp_in.jpg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_img.save(output_path)

    return output_path


def warp_out(paths: list) -> Path:
    with Image.open(paths[0]["frame_path"]) as img:
        output_img = img.convert("RGB")

    output_path = filtereds_frames_dir / f"_warp_out.jpg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_img.save(output_path)

    return output_path
