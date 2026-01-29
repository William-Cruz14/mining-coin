import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import psutil
import pandas as pd
from decouple import config

URL = config("URL")
BATS = {
    "XMR": r"C:\Users\Admin\Downloads\xmrig-6.25.0-windows-x64\miningXMR.bat",
    "QRL": r"C:\Users\Admin\Downloads\xmrig-6.25.0-windows-x64\miningQRL.bat",
    "ZEPH": r"C:\Users\Admin\Downloads\xmrig-6.25.0-windows-x64\miningZEPH.bat",
    "XTM" : r"C:\Users\Admin\Downloads\xmrig-6.25.0-windows-x64\miningXTM.bat"
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
    driver.get(URL)

    # Espere a página carregar completamente
    time.sleep(8)

    # Seleciona o botão "Adicionar processador" e clica nele
    button = driver.find_element(By.XPATH, "//div/button[text()='Adicionar processador']")
    button.click()
    # Preenche o formulário de busca e seleciona os processadores desejados
    input_form = driver.find_element(By.XPATH, "//input[@placeholder='Buscar modelo...']")
    input_form.send_keys("Ryzen 5 5600")
    select_amd = driver.find_element(By.XPATH, "//div//span[text()='RYZEN 5 5600']")
    select_amd.click()
    input_form.clear()

    input_form.send_keys("Xeon E5-2680 v4")
    select_intel = driver.find_element(By.XPATH, "//div//span[text()='XEON E5-2680 V4']")
    select_intel.click()

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")


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
    time.sleep(5)

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

            md = df.head(5) # Pega as 5 moedas mais rentáveis
            
            for index, row in md.iterrows():
                if row["Moeda"] in BATS:
                    if row["Ganho por Dia"] > ganho_aux:
                        ganho_aux = row["Ganho por Dia"]
                        moeda_rentavel = row["Moeda"]

            if moeda_rentavel:
                print(f"Moeda mais rentável para mineração: {moeda_rentavel} com ganho diário de R$ {ganho_aux:.2f}")
                iniciar_mineracao(moeda_rentavel)
                
            else:
                print("Nenhuma moeda rentável encontrada para mineração.")

            time.sleep(2 * 60 * 60)  # Espera por 2 horas antes de verificar novamente
            
        except KeyboardInterrupt:
            print("\nEncerrando o Script...")
            break