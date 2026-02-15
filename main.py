import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import psutil
import pandas as pd
from decouple import config
from selenium.webdriver.support.wait import WebDriverWait

from utils.email_setup import send_email

URL = config("URL")
BATS = {
    "XMR": r"C:\Users\Admin\Downloads\xmrig-6.25.0-windows-x64\miningXMR.bat",
    "QRL": r"C:\Users\Admin\Downloads\xmrig-6.25.0-windows-x64\miningQRL.bat",
    "ZEPH": r"C:\Users\Admin\Downloads\xmrig-6.25.0-windows-x64\miningZEPH.bat",
    "XTM": r"C:\Users\Admin\Downloads\xmrig-6.25.0-windows-x64\miningXTM.bat"
}
POOLS = {
    "QRL": "https://qrl.herominers.com/",
    "XMR": "https://monero.herominers.com/",
    "ZEPH": "https://zephyr.herominers.com/",
    "XTM": "https://pool.kryptex.com/pt-br/xtm-rx"
}
data = []
processo_xmrig = None


def limpar_numero(texto):
    return float(
        texto.replace("R$", "")
        .replace("/dia", "")
        .replace("/mês", "")
        .replace(",", ".")
        .strip()
    )


def fetch_cpu_rentability():
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

        ganho_dia = limpar_numero(ganhos[0].text)
        ganho_mes = limpar_numero(ganhos[1].text)

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


def parar_mineracao():
    for proc in psutil.process_iter(['pid', 'name']):
        if "xmrig" in proc.info['name'].lower():
            proc.kill()
            print(f"Processo {proc.info['name']} encerrado.")


def iniciar_mineracao(moeda):
    global processo_xmrig

    if moeda not in BATS:
        print("Moeda desconhecida")
        return

    parar_mineracao()
    time.sleep(10)  # Aguarde um pouco para garantir que o processo foi encerrado

    send_email(moeda=moeda.upper(), pool=POOLS[moeda])
    print(f"Iniciando mineração: {moeda.upper()}")

    processo_xmrig = subprocess.Popen(
        [BATS[moeda]],
        shell=True,
    )


if __name__ == '__main__':
    while True:
        try:
            fetch_cpu_rentability()
            df = pd.DataFrame(data)
            ganho_aux = 0.0
            moeda_rentavel = None

            for index, row in df.iterrows():
                if row["Moeda"] in BATS:
                    if row["Ganho por Dia"] > ganho_aux:
                        ganho_aux = row["Ganho por Dia"]
                        moeda_rentavel = row["Moeda"]

            if moeda_rentavel:
                print(f"Moeda mais rentável: {moeda_rentavel} com ganho diário de R$ {ganho_aux:.2f}")
                iniciar_mineracao(moeda_rentavel)
                print(df)
            else:
                print("Nenhuma moeda rentável encontrada.")

            time.sleep(2 * 60 * 60)  # Aguarde 2 horas antes de verificar novamente

        except KeyboardInterrupt:
            print("\nEncerrando o Script...")
            break
