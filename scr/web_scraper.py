import time
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.service import Service
from PIL import Image
from io import BytesIO
import pyautogui
import os
import glob
import zipfile
import shutil
import datetime
import random
import subprocess
import string

class descargaReportes():
    def __init__(self):
        self.directoryPath = os.getcwd()
        self.defaultPathDownloads = self.directoryPath + r'\temp'
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("prefs", {
            "download.default_directory": self.defaultPathDownloads,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })

        self.options.add_argument("--ignore-certificate-errors")
        self.url = "https://3eriza.nube.pe/"
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.maximize_window()

    def reiniciar(self):
        self.__init__()

    def login(self):
        self.driver.get(self.url)
        time.sleep(1)
    
    def iniciarSesion(self, username, password):
        wait = WebDriverWait(self.driver, 60)
        inputUser = wait.until(EC.presence_of_element_located((By.ID, "nombre")))
        inputUser.send_keys(username)
        time.sleep(2)

        inputPassword = self.driver.find_element(By.ID, "contrasenia")
        inputPassword.send_keys(password)
        time.sleep(2)

        btnLogIn = self.driver.find_element(By.XPATH, '//input[@value="Iniciar sesión"]')
        btnLogIn.click()

        wait=WebDriverWait(self.driver, 60)
        iframe_inicio=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class="iframebox"]')))
        self.driver.switch_to.frame(iframe_inicio)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class="sbscollapsepanel-header"]')))
        time.sleep(3)
        self.driver.switch_to.default_content()
        time.sleep(1)



    def validaInicioSesion(self):
        self.wait = WebDriverWait(self.driver, 60)
        self.menu_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[id="mod_btnmnu"]')))
        if self.menu_button:
            return True
        else:
            return False

    def cerrarSesion(self):
        menu = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[id="mod_btnmnu"]')))
        menu.click()
        time.sleep(1)

        toggle = self.driver.find_element(By.CSS_SELECTOR, '[class="dropdown-toggle media-body"]')
        toggle.click()
        time.sleep(1)

        btn_cerrar_sesion = self.driver.find_element(By.CSS_SELECTOR, '[id="usr_mnu_opc_3"]')
        btn_cerrar_sesion.click()
        time.sleep(1)

        btn_aceptar = self.driver.find_element(By.XPATH, '//span[@class="l-btn-text" and text()="Aceptar"]')
        btn_aceptar.click()
        time.sleep(3)
  
    def cantidad_excel(self):
        ruta_carpeta = self.defaultPathDownloads
        extension = '*.xlsx'
        patron_busqueda = os.path.join(ruta_carpeta, extension)
        archivos = glob.glob(patron_busqueda)
        cantidad_archivos = len(archivos)
        return cantidad_archivos
    
    # ====== 1. Reporte Excepciones ======
    def reporte_excepciones(self, empresa, fecha_inicio, fecha_fin):
        menu_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[id="mod_btnmnu"]')))
        menu_button.click()
        time.sleep(1)

        empresa = self.driver.find_element(By.XPATH, f'//a/span[text()="{empresa}"]')
        empresa.click()
        time.sleep(1)

        rrhh = self.driver.find_element(By.XPATH, '//li[@class="active"]/ul/li/a[text()="RR.HH.   "]')
        rrhh.click()
        time.sleep(1)

        monitor = self.driver.find_element(By.XPATH, '//li[@class="active"]/ul/li/ul/li/a[text()="MONITOR   "]')
        monitor.click()
        time.sleep(1)

        self.wait.until_not(EC.visibility_of_element_located((By.CSS_SELECTOR, '[id="loadingMsg"]')))
        #iframe
        iframe_element = self.wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[contains(@id, "mon-marcaciones")]')))
        self.driver.switch_to.frame(iframe_element)
        time.sleep(1)
        
        cantidad_excel_inicial = self.cantidad_excel()
        btn_descargar = self.wait.until(EC.presence_of_element_located((By.XPATH, '//span[@class="l-btn-icon icon-sbs-download-blue"]')))
        btn_descargar.click()

        #Valida que la descarga concluya
        cantidad_excel_final = cantidad_excel_inicial
        while cantidad_excel_final == cantidad_excel_inicial:
            time.sleep(1)
            cantidad_excel_final = self.cantidad_excel()
        else:
            pass

        time.sleep(1)

        self.driver.switch_to.default_content()
        self.driver.refresh()
        
        self.wait.until_not(EC.visibility_of_element_located((By.CSS_SELECTOR, '[id="loadingMsg"]')))
        time.sleep(1)

        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[id="mod_btnmnu"]')))
        time.sleep(1)


    # Funcion que reubicará las descargas en sus respectivas carpetas
    def renombrarReubicar(self, nuevoNombre, extension, carpetaDestino):
        ruta_descargas = self.directoryPath + r'/temp'
        archivos_descargados = sorted(glob.glob(os.path.join(ruta_descargas, '*')), key=os.path.getmtime, reverse=True)
        # Comprobar si hay archivos descargados
        if len(archivos_descargados) > 0:
            ultimo_archivo = archivos_descargados[0]
            # Cambiar el nombre del archivo --1er argumento de la funcion
            nuevo_nombre = f'{nuevoNombre}.{extension}' #xlsx, csv
            carpeta_destino = carpetaDestino
            # Comprobar si la carpeta de destino existe, si no, crearla
            if not os.path.exists(carpeta_destino):
                os.makedirs(carpeta_destino)
            # Ruta completa del archivo de destino
            ruta_destino = os.path.join(carpeta_destino, nuevo_nombre)
            # Mover el archivo a la carpeta de destino con el nuevo nombre
            shutil.move(ultimo_archivo, ruta_destino)

    # Funcion que crea el nombre del reporte
    def nombreReporte(self, name, finicio, ffin, fechaD0 = True):
        if fechaD0:
            fechaHora = datetime.datetime.now()
            fecha = fechaHora.strftime("%Y%m%d_%H%M%S")
            aleatorio = str(random.randint(100, 999))
            nameFile = name + fecha + '_' + aleatorio
        else:
            if ffin == None:
                ffin = finicio
            else:
                pass
            h = datetime.datetime.now()
            hora = h.strftime('%H%M%S')
            fechan = datetime.datetime.strptime(ffin, '%Y-%m-%d')
            fechan = fechan + datetime.timedelta(days=1)
            fecha = fechan.strftime("%Y%m%d_")
            aleatorio = str(random.randint(100, 999))
            nameFile = name + fecha + hora + '_' + aleatorio
        
        return nameFile

    def limpia_carpeta_descargas(self):
        # Ruta de la carpeta
        directorio_a_limpiar = self.defaultPathDownloads

        # Itera sobre todos los archivos en la carpeta
        for nombre_archivo in os.listdir(directorio_a_limpiar):
            ruta_completa = os.path.join(directorio_a_limpiar, nombre_archivo)

            # Verifica si es un archivo (ignorando subdirectorios)
            if os.path.isfile(ruta_completa):
                # Elimina el archivo
                os.remove(ruta_completa)
                print(f"Archivo eliminado: {ruta_completa}")


    def gameOver(self):
        self.driver.quit()







