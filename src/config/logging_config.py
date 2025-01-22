import logging

def setup_logging():
    """
    Configura e inicializa o sistema de logging da aplicação.
    
    Returns:
        logging.Logger: Logger configurado para uso na aplicação
    """
    logging.basicConfig(
        level=logging.ERROR,
        encoding='utf-8',
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )
    
    # Cria e retorna um logger específico para a aplicação
    logger = logging.getLogger('facebook_frame_bot')
    return logger 