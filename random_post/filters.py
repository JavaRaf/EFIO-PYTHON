from PIL import Image
from pathlib import Path


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
    """Espelha a imagem"""
    pass


def negative_filter(paths: list) -> Path:
    """Aplica um filtro negativo"""
    pass


def generate_palette(paths: list) -> Path:
    pass


def warp_in(paths: list) -> Path:
    pass


def warp_out(paths: list) -> Path:
    pass
