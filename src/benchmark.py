from benchmark_provider import BenchmarkProvider
from machine_attributes import Machine
from statistics import median
from logger import get_logger


logger = get_logger("benchmark-script")

class BenchmarkMatcher:

    
    def __init__(self, benchmark, machine):
        self.benchmark = benchmark
        self.machine = machine

    def select_hashrate(self):
        try:
            hashrates = sorted([spec.hashrate for spec in self.benchmark])
            print(hashrates)
            rm = int(len(hashrates) * 0.1)
            hashrates_filter = hashrates[rm:]
            return median(hashrates_filter)
        except Exception as e:
            logger.error(f"Erro ao fazer o match dos benchmarks: {e}")
            raise

if __name__ == "__main__":
    new_machine = Machine()
    bench = BenchmarkProvider(new_machine)
    match = BenchmarkMatcher(benchmark=bench.full_benchmarks(), machine=new_machine)
    print(match.select_hashrate())