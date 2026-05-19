from cpuinfo import get_cpu_info
from logger import get_logger
import platform
import psutil

logger = get_logger("benchmark-script")

class Machine:
    """
    Classe que representa uma máquina
    """

    @property
    def os_system(self):
        """
        Método que retorna o sistema operacional da máquina
        Returns:
            str: Sistema operacional da máquina
        """
        try:
            logger.info("Buscando o sistema operacional da máquina.")
            info = platform.system()
            return info
        except Exception as e:
            logger.error(f"Erro ao buscar o sistema operacional: {e}")
            raise


    @property
    def processor(self) -> str:
        """
        Método que retorna o processador da máquina
        Returns:
            str: Processador da máquina
        """
        
        try:
            logger.info("Buscando o processador da máquina.")
            cpu_info = get_cpu_info()
            return cpu_info.get('brand_raw', 'Unknown')
        except Exception as e:
            logger.error(f"Erro ao buscar o nome do processador: {e}")
            raise

    @property
    def cpu_cores(self):
        try:
            logger.info("Buscando a quantidade de núcleos do processador.")
            return psutil.cpu_count(logical=False)
        except Exception as e:
            logger.error(f"Erro ao buscar a quantidade de núcleos do processador: {e}")
            raise

    @property
    def cpu_threads(self):
        try:
            logger.info("Buscando a quantidade de threads do processador.")
            return psutil.cpu_count(logical=True)
        except Exception as e:
            logger.error(f"Erro ao buscar a quantidade de threads do processador: {e}")
            raise

    @property
    def memory(self) -> float:
        """
        Método que retorna a memória da máquina
        Returns:
            float: Memória da máquina
        """

        try:
            logger.info("Buscando a quantidade de ram da máquina.")
            memory = psutil.virtual_memory().total / (1024 ** 3)
            return memory
        except Exception as e:
            logger.error(f"Erro ao buscar a quantidade de ram: {e}")
            raise
    
            
if __name__ == "__main__":
    machine = Machine()
    print(machine.os_system)
    print(machine.processor)