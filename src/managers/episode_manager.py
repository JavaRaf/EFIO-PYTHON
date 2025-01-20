from ruamel.yaml import YAML


def update_episode_progress(config: dict) -> dict:
    """
    Updates the posted frames progress and manages episode transitions.
    
    Args:
        config (dict): Configuration dictionary containing episode information
        
    Returns:
        dict: Updated configuration
    """
    config["total_frames_posted"] += config.get("posting")["fph"]
    current_episode_index = config.get("current_episode") - 1
    config["episodes"][current_episode_index]["frame_iterator"] += config.get("posting")["fph"]
    
    if config["episodes"][current_episode_index]["frame_iterator"] >= config["episodes"][current_episode_index]["episode_total_frames"]:
        print(f"Episódio {config['current_episode']} finalizado", flush=True)
        config["episodes"][current_episode_index]["completed"] = True
        
        next_episode_index = current_episode_index + 1
        if next_episode_index < len(config["episodes"]):
            if config["episodes"][next_episode_index]["episode_total_frames"] > 0:
                config["current_episode"] += 1
                print(f"Iniciando episódio {config['current_episode']}", flush=True)
            else:
                print("Próximo episódio não está configurado (episode_total_frames = 0)", flush=True)
        else:
            print("Não há mais episódios disponíveis", flush=True)


    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 1000

    with open("Configs.yaml", "w") as file:
        yaml.dump(config, file)

    return config