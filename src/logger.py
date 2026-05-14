import logging

def get_logger(name: str):
    """
    Configura o logger para registrar mensagens de log em um arquivo e no console.
    Args:
        name (str): O nome do logger.
    
    """
    logging.basicConfig(
        filename="../log-script.log",
        encoding="utf-8",
        level=logging.INFO,
        format="{asctime} - {levelname} - {name} - {message}",
        style="{",
        datefmt="%d/%m/%Y %H:%M"
    )
    
    return logging.getLogger(name)

if __name__ == "__main__":
    logger = get_logger(__name__)
    logger.info("Testando o logger")