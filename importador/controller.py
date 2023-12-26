import os
from util.email import Email
import json
import glob
from datetime import datetime, timedelta
from service.ReportService import ReportService

mReport = ReportService()
properties = mReport.getProperties()

# Obtenemos el nombre del archivo
# filePath = r'/home/renovaciones/3ERIZA_RENOVACIONES_ALL.csv'
ROOT_PATH = properties['LOAD_PATH']

FILES_PATH = []
FILES_NOT_FOUND = []

jsonDataReports = './importador/prueba.json'

with open(jsonDataReports, "r") as json_file:
    data = json.load(json_file)

    for platform in data['planiweb']:        
        # Extraemos la plataforma
        
        for campaign in data['planiweb'][str(platform)]:
            campana = campaign["campaign"]
            print('Campana : ' + campana)
            for reporte in campaign["reports"]:
                codigo = reporte["code"]
                properties = reporte["properties"]
                tipo = reporte["tipo"]
                anadir_fecha = reporte["anadir_fecha"]
                anadir_anio = reporte["anadir_anio"]
                data_base = reporte["data_base"]

                skip_rows = reporte["skip_rows"]
                print("Reporte:", codigo)
                
                directoryPath = ROOT_PATH  + platform + "\\" + codigo
                currentDate = datetime.now().strftime("%Y%m%d")
                #print(directoryPath)
                currentDate = '20231226'

                # Los reportes son al d-1 por eso la fecha insert es al curdate-1
                fecha_insert = None
                if anadir_fecha:
                    fecha_objeto = datetime.strptime(currentDate, "%Y%m%d")
                    fecha_objeto_modificada = fecha_objeto - timedelta(days=1)
                    fecha_insert = fecha_objeto_modificada.strftime("%Y-%m-%d")
                else:
                    pass
                
                anio_insert = None
                if anadir_anio:
                    fecha_objeto = datetime.strptime(currentDate, "%Y%m%d")
                    fecha_objeto_modificada = fecha_objeto - timedelta(days=1)
                    anio_insert = fecha_objeto_modificada.strftime("%Y")
                else:
                    pass
                
                # Patron de coincidencia para los nombres de archivo
                patron = f"*_{currentDate}_*"
                archivos_coincidentes = glob.glob(os.path.join(directoryPath, patron))
                

                if(archivos_coincidentes):
                    
                    file = {
                        'name': platform + "\\" + codigo + '\\' + patron,
                        'path' : archivos_coincidentes[0],
                        'table' : codigo, # salesforce_1261mov1
                        'db': data_base,
                        'properties' : properties,
                        'tipo': tipo,
                        'fecha_insert': fecha_insert,
                        'anio_insert': anio_insert,
                        "skip_rows": skip_rows,
                        "grupo": campana,
                        "code": codigo
                    }
                    
                    FILES_PATH.append(file)
                else:
                    FILES_NOT_FOUND.append(campana +  platform + "\\" + codigo + '\\' + patron)

if( FILES_NOT_FOUND ):
    strFiles = '<br>'.join(FILES_NOT_FOUND)  
    print("No se encontraron archivos de reporte: " + strFiles)        
    email = Email('text')
    cc_email = {
        'cc_list' : ['soporte@qnextplus.com'],
        'bcc_list' : ['isac.delacruz@3eriza.pe']#,'michael.luque@3eriza.pe']
    }   
    email.send('Robotin - REPORTES','&#x274C; No se encontraron archivos de reporte: <br>' + strFiles,'luquemichael.92@gmail.com' ,cc_email)    
    exit()

for file in FILES_PATH:        
    result = mReport.loadData(file['path'], file['table'], file['db'], file['tipo'], file['fecha_insert'], file['anio_insert'], file['grupo'], file["code"], file['skip_rows'], file['properties']['dbType'], file['properties']['renameColumns'], file['properties']['converters'])

    if(result=='400'):
        email = Email('text')
        cc_email = {
            'cc_list' : ['soporte@qnextplus.com'],
            'bcc_list' : ['isac.delacruz@3eriza.pe','michael.luque@3eriza.pe']
        }   
        email.send('Robotin - REPORTES','&#x274C; Hubo un problema al importar los datos del archivo <strong>' + file['name'] + "</strong>",'luquemichael.92@gmail.com' ,cc_email) 

print("Se ejecuto correctamente todas las consultas del dia " + currentDate)
exit()