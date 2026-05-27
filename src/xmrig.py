import platform
import subprocess
import tarfile
import zipfile
from pathlib import Path

import psutil
from decouple import config
from playwright.sync_api import sync_playwright

from coins import Coin
from discord_notification import send_discord_notification
from email_setup import send_email
from logger import get_logger

logger = get_logger("xmrig-download-script")

IS_LINUX = platform.system() == "Linux"

class Miner:
    BASE_DIR = Path(__file__).parent.parent
    VERSION = "6.26.0"

    def __init__(self, version=None):
        self.version = version or self.VERSION
        if IS_LINUX:
            self.file_name = f"xmrig-{self.version}-linux-static-x64.tar.gz"
        else:
            self.file_name = f"xmrig-{self.version}-windows-x64.zip"
        self.dir_download = self.BASE_DIR / 'download'
        self.dir_file = self.dir_download / self.file_name
        self.dir_miner = self.BASE_DIR / 'miner'

    def _verify_download(self) -> bool:
        if not self.dir_file.exists():
            logger.error(f"Arquivo {self.dir_file.name} não encontrado.")
            return False
        logger.info(f"Arquivo {self.dir_file.name} encontrado.")
        return True

    def _verify_unzipped_file(self) -> bool:
        if not self.dir_miner.exists() or not any(self.dir_miner.glob("*xmrig*")):
            logger.error("Arquivo não foi descompactado.")
            return False
        logger.info("Arquivo descompactado com sucesso.")
        return True

    def _xmrig_executable(self) -> Path:
        binary = "xmrig" if IS_LINUX else "xmrig.exe"
        return self.dir_miner / f"xmrig-{self.version}" / binary

    def download_xmrig(self):
        try:
            self.dir_download.mkdir(parents=True, exist_ok=True)
            self.dir_miner.mkdir(parents=True, exist_ok=True)

            if not self._verify_download():
                with sync_playwright() as play:
                    browser = play.chromium.launch(headless=True, slow_mo=50)
                    page = browser.new_page()
                    page.goto("https://xmrig.com/download")

                    if IS_LINUX:
                        page.get_by_role("button").filter(has_text="linux-static-x64.tar.gz").click()
                    else:
                        page.get_by_role("button").filter(has_text="x64.zip").click()

                    page.get_by_role("button").filter(has_text="link").click()

                    with page.expect_download() as download_file:
                        page.get_by_role("dialog").locator("a.btn.btn-success").click()
                    download_xmrig = download_file.value

                    download_xmrig.save_as(self.dir_file)
                    page.wait_for_timeout(9000)
                    browser.close()
                logger.info("Arquivo baixado com sucesso.")

            self._extract_file(self.dir_file, self.dir_miner)

        except Exception as e:
            logger.error(f"Erro ao baixar o XMRig: {e}")
            raise

    def _extract_file(self, archive_path: Path, extract_to: Path):
        try:
            Path(extract_to).mkdir(parents=True, exist_ok=True)

            if self._verify_unzipped_file():
                logger.info("Arquivo já foi descompactado.")
                return

            if IS_LINUX and tarfile.is_tarfile(archive_path):
                with tarfile.open(archive_path, 'r:gz') as tar:
                    def is_safe(member, dest):
                        dest_path = Path(dest).resolve()
                        member_path = (dest_path / member.name).resolve()
                        return member_path.is_relative_to(dest_path)
                    safe_members = [
                        m for m in tar.getmembers() if is_safe(m, extract_to)]

                    tar.extractall(extract_to, members=safe_members)
                self._xmrig_executable().chmod(0o755)
                logger.info(f"Arquivo extraído com sucesso em: {extract_to}")

            elif zipfile.is_zipfile(archive_path):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    for member in zip_ref.namelist():
                        member_path = Path(extract_to) / member
                        if not member_path.resolve().is_relative_to(
                                Path(extract_to).resolve()):
                            logger.error(f"Entrada inválida no zip: {member}")
                            raise ValueError(f"Entrada inválida no zip: {member}")
                    zip_ref.extractall(extract_to)
                    logger.info(f"Arquivo descompactado com sucesso em: {extract_to}")

        except Exception as e:
            logger.error(f"Erro ao extrair o arquivo: {e}")
            raise

    # Mantido por compatibilidade, delega para _extract_file
    def unzip_file(self, zip_path, extract_to):
        self._extract_file(Path(zip_path), Path(extract_to))

    def stop_miner(self):
        for proc in psutil.process_iter(['pid', 'name']):
            if "xmrig" in proc.info['name'].lower():
                proc.kill()
                logger.info(f"Processo {proc.info['name']} encerrado.")

    def start_miner(self, coin: Coin, threads: int):
        logger.info("Iniciando mineração com XMRig.")
        logger.info(
            f"Moeda: {coin.name} | "
            f"Algoritmo: {coin.algorithm} | Pool: {coin.pool}")
        try:
            self.download_xmrig()
            logger.info("Parando mineração caso ela já esteja rodando.")
            self.stop_miner()

            logger.info("Iniciando o processo de mineração.")

            kwargs = {}
            if not IS_LINUX:
                kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE

            process = subprocess.Popen(
                [
                    str(self._xmrig_executable()),
                    "-a", coin.algorithm,
                    "-o", coin.pool,
                    "-u", coin.wallet,
                    "-p", "x",
                    "-k",
                    "--tls",
                    "--threads", f"{threads}",
                ],
                **kwargs,
            )

            send_email(coin.name, coin.site)
            send_discord_notification(
                config("DISCORD_WEBHOOK_URL"),
                f"Mineração iniciada com sucesso! Moeda: {coin.name}\n"
                f"Consulte no site da pool: {coin.site}")

            return process
        except Exception as e:
            logger.error(f"Erro ao iniciar o mineração: {e}")
            raise

    def switch_to_coin(self, coin: Coin, threads: int):
        try:
            logger.info("Alternando a moeda.")
            logger.info("Parando mineração.")
            logger.info(f"Alternando para a moeda: {coin.name}")
            self.stop_miner()
            self.start_miner(coin, threads)
        except Exception as e:
            logger.error(f"Erro ao alternar para a moeda: {e}")
            raise


if __name__ == "__main__":
    miner = Miner()
    miner.download_xmrig()
    miner.start_miner(Coin.XMR, threads=4)
