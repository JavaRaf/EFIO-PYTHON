import logging
import os

os.makedirs("utils/logs", exist_ok=True)

# Configuração básica do logger
logging.basicConfig(
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("utils/logs/error.log"), logging.StreamHandler()],
)


# Função para obter o logger
def get_logger(name):
    return logging.getLogger(name)


logger = get_logger(__name__)