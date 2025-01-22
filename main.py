import time
from src.config.config_loader import load_necessary_configs, parse_config
from src.integrations.facebook import fb_post, fb_update_bio
from src.utils.subtitle_handler import extract_all_subtitles
from src.utils.frame_utils import generate_random_frame_crop
from src.utils.message_formatter import format_post_message
from src.services.frame_service import build_frame_file_path
from src.managers.episode_manager import update_episode_progress
from utils.logger import log_facebook_interaction
from src.config.config_loader import load_necessary_configs
from src.config.logging_config import setup_logging

# Inicializa o logger
logger = setup_logging()

def main():
    """
    Função principal que gerencia o processo de postagem de frames no Facebook.
    
    O programa realiza as seguintes operações:
    1. Carrega e valida as configurações
    2. Posta frames sequencialmente com legendas (se configurado)
    3. Gera e posta crops aleatórios (se configurado)
    4. Atualiza o progresso do episódio
    5. Atualiza a biografia da página
    """
    try:
        # Carrega e valida configurações
        config = parse_config("configs.yaml")
        fph, frame_intarator, post_interval, current_time = load_necessary_configs(config)  
        logs_fb = []
        print(f"Iniciando execução em {current_time}", flush=True)
    except Exception as e:
        logger.error(f"Erro ao carregar configurações: {str(e)}")

    try:
        for post in range(1, fph + 1):
            
            frame_number = frame_intarator + post
            frame_path = build_frame_file_path(frame_number, config)

            if frame_path:
                # Posta frame
                post_message = format_post_message(frame_number, config.get("templates").get("post_message"), config)
                post_id = fb_post(post_message,frame_path=frame_path, config=config)
                print(f"frame {frame_number} posted", flush=True)

                time.sleep(2)

                # Posta legendas
                if config.get("posting").get("posting_subtitles"):
                    subtitle_message = extract_all_subtitles(frame_number, config)
                    # Verifica se há legendas para postar
                    if subtitle_message:
                        for subtitle in subtitle_message:
                            fb_post(subtitle, parent_id=post_id, config=config)
                            print(f"subtitle of frame {frame_number} posted", flush=True)

                        time.sleep(2)

                # Posta crops aleatórios
                if config.get("posting").get("random_crop"):
                    crop_path, crop_message = generate_random_frame_crop(frame_path,frame_number, config)
                    fb_post(crop_message, frame_path=crop_path, parent_id=post_id, config=config)
                    print(f"random crop of frame {frame_number} posted", flush=True)

                    time.sleep(2)

                # salva a interação do Facebook para futura logagem
                logs_fb.append((config.get("current_episode"), frame_number, post_id))

                # espera o intervalo de postagem (2 minutos default)
                time.sleep(post_interval * 2) 

        # Atualiza o progresso do episódio se não está em modo random_posting
        if not config.get("posting").get("random_posting"):
            update_episode_progress(config) # consetar isso aqui depois
            log_facebook_interaction(current_time, logs_fb)

        # Atualiza a biografia da página
        bio_message = format_post_message(frame_number, config.get("templates").get("bio_message"), config)
        fb_update_bio(bio_message, config)

        

    except Exception as e:
        logger.error(f"Erro ao postar frames: {str(e)}")

    

if __name__ == "__main__":
    main()
