from statistics import median, mode

from benchmark_provider import BenchmarkProvider
from logger import get_logger
from machine_attributes import Machine
from power_cpu import CPU_DATABASE

logger = get_logger("benchmark-script")

class BenchmarkMatcher:
    """
    Classe que faz o match entre o benchmark e a máquina
    """
    
    def __init__(self, benchmark, machine):
        self.benchmark = benchmark
        self.machine = machine

    def select_hashrate(self) -> int:
        """
        Método que retorna o hashrate da máquina
        Returns:
            int: Hashrate da máquina
        """
        try:
            logger.info("Fazendo o match dos benchmarks com a máquina")
            hashrates = sorted([spec.hashrate for spec in self.benchmark])
            limit = int(len(hashrates) * 0.1)
            hashrates_filter = hashrates[limit:]
            return round(median(hashrates_filter))
        except Exception as e:
            logger.error(f"Erro ao fazer o match dos benchmarks: {e}")
            raise

    def select_power(self) -> int:
        """
        Método que retorna a potência do processador
        Returns:
            power_cpu: Potência do processador
        """
        try:
            logger.info("Buscando a potência do processador")
            power_cpu = 0
            for key,value in CPU_DATABASE.items():
                if key in self.machine.processor:
                    power_cpu += value

            return power_cpu
        except Exception as e:
            logger.error(f"Erro ao buscar a potência do processador: {e}")
            raise


    def select_threads(self):
        """
        Método que retorna a quantidade de threads da máquina
        Returns:
            int: Quantidade de threads da máquina
        """
        try:
            logger.info("Buscando a quantidade de threads da máquina")
            threads = [spec.threads for spec in self.benchmark ]
            return mode(threads)
        except Exception as e:
            logger.error(f"Erro ao buscar a quantidade de threads: {e}")
            raise


if __name__ == "__main__":
    new_machine = Machine()
    bench = BenchmarkProvider(new_machine)
    match = BenchmarkMatcher(benchmark=bench.full_benchmarks(), machine=new_machine)
    print(match.select_hashrate())
    print(match.select_power())
    print(match.select_threads())