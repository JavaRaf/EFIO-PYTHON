import logging
import os

# Cria o diretório sys se não existir
os.makedirs("sys", exist_ok=True)

# Configuração básica do logger
logging.basicConfig(
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("sys/Error.log"), logging.StreamHandler()],
)


# Função para obter o logger
def get_logger(name):
    return logging.getLogger(name)
