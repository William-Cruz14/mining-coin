from datetime import datetime
from http import HTTPStatus

import requests

from logger import get_logger
from dto_specs import BenchFull, BenchResume
from machine_attributes import Machine

logger = get_logger("benchmark-provider-script")

class BenchmarkProvider:
    """
    Classe que representa o provider do benchmark
    """

    def __init__(self, machine):
        self.machine = machine

    def benchmarks(self) -> list[BenchResume]:
        """
        Método que retorna os ids dos benchmarks
        Returns:
            list[BenchResume]: Lista com os objetos BenchResume
        """

        try:
            resumes = []
            response = requests.get(f"https://api.xmrig.com/1/benchmarks?cpu={self.machine.processor}")
            if response.status_code == HTTPStatus.OK:
                for bench in response.json():
                    conditions_to_test = [
                        bench["threads_ok"] == True,
                        bench["os"] == self.machine.os_system.lower(),
                        bench["version"] >= "6.20.0",
                        bench["done_ts"] is not None,
                        bench["cpu"]["packages"] == 1
                    ]

                    if all(conditions_to_test):
                        done_ts = datetime.fromtimestamp(bench['done_ts'] / 1000)
                        if done_ts.year >= datetime.now().year - 2:
                            resumes.append(
                                BenchResume(
                                    id=bench['id'],
                                    threads_ok=bench['threads_ok'],
                                    done_ts=done_ts,
                                    version=bench['version'],
                                    os=bench['os'],
                                    cpu_count=bench['cpu']['packages']
                                )
                            )
            print(resumes)
            return resumes
        except Exception as e:
            logger.error(f"Ocorreu um erro ao buscar os benchmarks: {e}")
            raise
                
    def full_benchmarks(self) -> list[BenchFull]:
        """
        Método que retorna os atributos dos benchmarks
        Returns:
            list[Specs]: Lista de objetos Specs
        """

        try:
            attributes = []
            logger.info("Buscando atributos dos benchmarks.")
            bench_marks = self.benchmarks()

            for bench in bench_marks:
                memory_size = 0
                link = f"https://api.xmrig.com/1/benchmark/{bench.id}"
                response = requests.get(link)

                if response.status_code == HTTPStatus.OK:
                    data = response.json()

                    dmi_memory = (data.get("dmi") or {}).get("memory") or []
                    for mem in dmi_memory:
                        if mem.get("size"):
                            memory_size += mem["size"] / (1024 ** 3)


                    conditions_to_test = [
                        data["done_ts"] is not None,
                        memory_size >= round(self.machine.memory),
                        data["cpu"]["threads"] == self.machine.cpu_threads,
                        data["cpu"]["cores"] == self.machine.cpu_cores,
                    ]

                    if all(conditions_to_test):

                        done_ts = datetime.fromtimestamp(data['done_ts'] / 1000)

                        attributes.append(
                            BenchFull(
                                os= data['os'],
                                ram= memory_size,
                                done_ts= done_ts,
                                hashrate= data['hashrate'],
                                threads= data['threads'],
                                cpu_cores=data['cpu']['cores'],
                                cpu_threads=data['cpu']['threads']

                            )
                        )
            
            return attributes
        
        except Exception as e:
            logger.error(f"Erro ao setar count processor: {e}")
            raise
            
if __name__ == "__main__":
    new_machine = Machine()
    benchmark = BenchmarkProvider(machine=new_machine)
    print(benchmark.full_benchmarks())