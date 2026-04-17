import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from decouple import config
from selenium.webdriver.support.wait import WebDriverWait
from utils.email_setup import send_email
from utils.discord_notification import send_discord_notification
import time
import psutil
import pandas as pd

URL = config("URL")
BATS = {
    "XMR": r"C:\Users\willi\Downloads\Miner\xmrig-6.25.0-windows-x64\miningXMR.bat",
    "QRL": r"C:\Users\willi\Downloads\Miner\xmrig-6.25.0-windows-x64\miningQRL.bat",
    "ZEPH": r"C:\Users\willi\Downloads\Miner\xmrig-6.25.0-windows-x64\miningZEPH.bat",

    #"XMR": r"C:\Users\Admin\Downloads\xmrig-6.25.0-windows-x64\miningXMR.bat",
    #"QRL": r"C:\Users\Admin\Downloads\xmrig-6.25.0-windows-x64\miningQRL.bat",
    #"ZEPH": r"C:\Users\Admin\Downloads\xmrig-6.25.0-windows-x64\miningZEPH.bat",

}
POOLS = {
    "QRL": "https://qrl.herominers.com/",
    "XMR": "https://monero.herominers.com/",
    "ZEPH": "https://zephyr.herominers.com/"
}

FIRST_STEP = True


def clean_number(texto):
    return float(
        texto.replace("R$", "")
        .replace("/dia", "")
        .replace("/mês", "")
        .replace(",", ".")
        .strip()
    )


def fetch_cpu_rentability():
    try:
        data = []
        driver = webdriver.Chrome()
        driver.get(URL)  # Acesse a página de rentabilidade de mineração de CPU
        wait = WebDriverWait(driver, 15)  # Espera de até 15 segundos para os elementos aparecerem

        # Seleciona o botão "Adicionar processador" e clica nele
        button = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div/button[text()='Adicionar processador']")
            )
        )
        button.click()
        time.sleep(5)
        # Preenche o formulário de busca e seleciona os processadores desejados
        input_form = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='Buscar modelo...']")
            )
        )
        input_form.send_keys("Ryzen 5 5600")
        select_amd = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[text()='RYZEN 5 5600']")
            )
        )
        select_amd.click()
        time.sleep(5)
        input_form.clear()
        time.sleep(5)

        input_form.send_keys("Xeon E5-2680 v4")
        select_intel = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[text()='XEON E5-2680 V4']")
            )
        )
        select_intel.click()

        rows = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "tbody tr")
            )
        )

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")

            moeda = cols[0].find_element(By.CLASS_NAME, "text-white").text
            algoritmo = cols[0].find_element(By.CLASS_NAME, "text-zinc-400").text

            spans = cols[1].find_elements(By.TAG_NAME, "span")
            hashrate = spans[0].text
            hashrate_unit = spans[1].text

            consumo = int(cols[2].find_element(By.TAG_NAME, "span").text)

            ganhos = cols[4].find_elements(By.TAG_NAME, "div")

            ganho_dia = clean_number(ganhos[0].text)
            ganho_mes = clean_number(ganhos[1].text)

            data_temp = {
                "Moeda": moeda,
                "Algoritmo": algoritmo,
                "Hashrate": hashrate,
                "Hashrate Unit": hashrate_unit,
                "Consumo W": consumo,
                "Ganho por Dia": ganho_dia,
                "Ganho por Mês": ganho_mes,
            }

            data.append(data_temp)

        time.sleep(10)
        driver.quit()
        return data

    except Exception as e:
        print(f"Erro ao buscar dados: {e}")



def stop_miner():
    # Encerra o processo do XMRig, se estiver rodando
    for proc in psutil.process_iter(['pid', 'name']):
        if "xmrig" in proc.info['name'].lower():
            proc.kill()
            print(f"Processo {proc.info['name']} encerrado.")


def initialize_miner(coin):
    if coin not in BATS:
        print("Moeda desconhecida")
        return None

    stop_miner()
    time.sleep(10)  # Aguarde um pouco para garantir que o processo foi encerrado

    send_discord_notification()
    send_email(coin=coin.upper(), pool=POOLS[coin])
    print(f"Iniciando mineração: {coin.upper()}")

    process_xmrig = subprocess.Popen(
        [BATS[coin]],
        shell=True,
    )

    return process_xmrig


if __name__ == '__main__':
    coin_max = pd.Series() # Variável para armazenar a moeda mais rentável encontrada até o momento
    coin_rentable_sigla, coin_rentable_win = None, None # Variáveis para armazenar a sigla e o ganho diário da moeda mais rentável
    coin_current = pd.Series() # Variável para armazenar a moeda atualmente minerada

    while True:
        try:
            data_finder = fetch_cpu_rentability() # Buscando a rentabilidade das moedas

            # Filtra apenas com as moedas que estão no dicionário BATS
            if not data_finder:
                print("Nenhuma moeda encontrada. Verifique a conexão ou a estrutura da página.")
                time.sleep(5 * 60)  # Aguarda 5 minutos antes de tentar novamente
                continue

            data_updated = pd.DataFrame(data_finder)

            if "Moeda" not in data_updated.columns or "Ganho por Dia" not in data_updated.columns:
                print("Colunas 'Moeda' ou 'Ganho por Dia' não encontradas no DataFrame. Verifique a estrutura dos dados.")
                time.sleep(5 * 60)  # Aguarda 5 minutos antes de tentar novamente
                continue

            data_updated_filtered = data_updated[data_updated["Moeda"].isin(BATS.keys())].sort_values(
                by="Ganho por Dia",
                ascending=False
            ).reset_index(drop=True)

            if data_updated_filtered.empty:
                print("Nenhuma moeda rentável encontrada. Verifique os dados ou a estrutura da página.")
                time.sleep(5 * 60)  # Aguarda 5 minutos antes de tentar novamente
                continue

            coin_top = data_updated_filtered.iloc[0]  # Seleciona a moeda mais rentável do DataFrame atualizado

            if FIRST_STEP or coin_max.empty:
                FIRST_STEP = False
                coin_max = coin_top # Seleciona a moeda mais rentável do DataFrame filtrado.
                coin_rentable_sigla = coin_max["Moeda"]
                coin_rentable_win = coin_max["Ganho por Dia"]
                print(f"Moeda mais rentável: {coin_rentable_sigla} com ganho diário de R$ {coin_rentable_win:.2f}")
                initialize_miner(coin_rentable_sigla)

            else:
                # Verifica a moeda atualmente minerada no DataFrame atualizado
                coin_current = data_updated_filtered[data_updated_filtered["Moeda"] == coin_rentable_sigla].iloc[0]

                print(coin_current)

                if coin_top["Moeda"] != coin_rentable_sigla:
                    if coin_top["Ganho por Dia"] > (coin_current["Ganho por Dia"] * 1.05):
                        coin_max = coin_top  # Seleciona a moeda mais rentável do DataFrame filtrado
                        coin_rentable_sigla = coin_max["Moeda"]
                        coin_rentable_win = coin_max["Ganho por Dia"]
                        print(f"Nova moeda mais rentável encontrada: {coin_rentable_sigla} com ganho diário de R$ {coin_rentable_win:.2f}")
                        initialize_miner(coin_rentable_sigla)
                else:
                    coin_max = coin_current
                    coin_rentable_sigla = coin_max["Moeda"]
                    coin_rentable_win = coin_max["Ganho por Dia"]
                    print(f"A moeda mais rentável continua sendo: {coin_rentable_sigla} com ganho diário de R$ {coin_rentable_win:.2f}")

            time.sleep( 2 * 60 * 60)  # Aguarda 2 horas antes de verificar novamente a rentabilidade das moedas


        except KeyboardInterrupt:
            print("\nEncerrando o Script...")
            break

        except Exception as e:
            print(f"Erro inesperado: {e}")
            time.sleep(5 * 60)  # Aguarda 5 minutos antes de tentar novamente
