import zipfile
import os
import glob

directorio_actual = os.getcwd()
directorio_zip = directorio_actual + r"\temp"
patron = "*.zip"
"""
# Ruta al archivo ZIP
archivos_zip = glob.glob(os.path.join(directorio_zip, patron))
archivo_zip = archivos_zip[0]
#exit()
directorio_destino = directorio_zip
with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
    zip_ref.extractall(directorio_destino)
"""
# Ruta de la carpeta
directorio_a_limpiar = directorio_actual + r"\temp"

# Itera sobre todos los archivos en la carpeta
for nombre_archivo in os.listdir(directorio_a_limpiar):
    ruta_completa = os.path.join(directorio_a_limpiar, nombre_archivo)

    # Verifica si es un archivo (ignorando subdirectorios)
    if os.path.isfile(ruta_completa):
        # Elimina el archivo
        os.remove(ruta_completa)
        print(f"Archivo eliminado: {ruta_completa}")
