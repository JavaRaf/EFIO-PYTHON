import random
from pathlib import Path

def build_frame_file_path(frame_number: int, config: dict) -> Path:
    """
    Constrói o caminho do arquivo para um frame específico ou aleatório de um episódio.
    
    Args:
        frame_number: Número do frame desejado
        config: Dicionário de configuração contendo:
            - current_episode: Número do episódio atual
            - posting.random_posting: Se True, retorna um frame aleatório
            - episodes[].total_frames: Número total de frames do episódio
    
    Returns:
        Path: Caminho do arquivo do frame
    
    Raises:
        FileNotFoundError: Se o arquivo do frame não existir
    """

    episode_num = config.get("current_episode")
    episode_dir = Path(f"episodes/frames/{episode_num:02d}")
    
    if not episode_dir.exists():
        raise FileNotFoundError(f"Diretório do episódio não encontrado: {episode_dir}")
    
    if config.get("posting")["random_posting"]:
        total_frames = config.get("episodes")[episode_num - 1].get("total_frames")
        frame_num = random.randint(1, total_frames)
    else:
        frame_num = frame_number
    
    # Tenta primeiro o formato com 4 dígitos
    frame_path = episode_dir / f"frame_{frame_num:04d}.jpg"
    
    # Se não encontrar, tenta o formato simples
    if not frame_path.exists():
        frame_path = episode_dir / f"frame_{frame_num}.jpg"
        
    if not frame_path.exists():
        raise FileNotFoundError(f"Arquivo do frame não encontrado: {frame_path}")
        
    return frame_path 