from web_scraper import descargaReportes
from isdb import TablaValidacion2
import time
import datetime
import subprocess

# Paso 1: Descarga de Reportes
#Rango de fechas para descarga de Reportes
D0 =  datetime.date.today()
D_1 =  D0 + datetime.timedelta(days=-1)
inicio = str(D_1) #'2023-08-04'
fin = str(D_1) #None#'2023-08-08'
currentDate = D0.strftime("%Y%m%d") # ojo para descarga de vacaciones - pendientes

fecD0 = False
username = "EDWIN_10139879"
password = "Planiweb2021peru!"

tablaValidacion = TablaValidacion2()
tablaValidacion.crearBD()
tablaValidacion.crearTabla()
tablaValidacion.truncateTable()

descarga = descargaReportes()
def logueo():
    descarga.login()
    descarga.iniciarSesion(username, password)
    inicioSesion = descarga.validaInicioSesion()

    while not inicioSesion:
        descarga.reiniciar()
        descarga.login()
        descarga.iniciarSesion(username, password)
        inicioSesion = descarga.validaInicioSesion()
    else:
        print('Inicio de Sesion Exitosa')
        pass
        
logueo()
empresa = {
    'bpo': 'BPO PERU S.A.C.',
    'terceriza': 'TERCERIZA PERU S.R.L.'
}

contador_descargas = 1

# ===== 1. Reporte Excepciones =====
for key, value in empresa.items():
    grupo = key
    razon_social = value

    fecD0 = False
    campana = "planiweb " + grupo
    # ===== I. Reporte Excepciones =====
    def re_excepciones():
        nombreAsignado = f'{grupo}_excepciones_'
        try:
            descarga.limpia_carpeta_descargas()
            descarga.reporte_excepciones(razon_social, inicio, fin)
            nombre = descarga.nombreReporte(nombreAsignado, inicio, fin, fecD0)
            destino = descarga.directoryPath + rf'/carga\{grupo}\excepciones'
            descarga.renombrarReubicar(nombre, 'xlsx', destino)

            datos=[(contador_descargas, campana, nombreAsignado, 1)]
            tablaValidacion.agregarVariosDatos(datos)
        except Exception as e:
            print('isdb_error: ', e)
            datos=[(contador_descargas, campana, nombreAsignado, 0)]
            tablaValidacion.agregarVariosDatos(datos)
            pass
    
    re_excepciones()
    ultimoRegistro = tablaValidacion.leerDatos()
    descargo = ultimoRegistro[0][3]

    while descargo == 0:
        tablaValidacion.deleteTable(contador_descargas)

        descarga.reiniciar()
        logueo()

        re_excepciones()
        ultimoRegistro = tablaValidacion.leerDatos()
        descargo = ultimoRegistro[0][3]
    else:
        contador_descargas += 1
        print(f"Descargo reporte {grupo} excepciones")
        pass

# ===== 2. Reporte Prestamos =====
empresa = {
    'bpo': 'BPO PERU S.A.C.'
}
for key, value in empresa.items():
    grupo = key
    razon_social = value

    fecD0 = False
    campana = "planiweb " + grupo

    def re_prestamos():
        nombreAsignado = f'{grupo}_prestamos_'
        try:
            descarga.limpia_carpeta_descargas()
            descarga.reporte_prestamos(razon_social, inicio, fin)
            nombre = descarga.nombreReporte(nombreAsignado, inicio, fin, fecD0)
            destino = descarga.directoryPath + rf'/carga\{grupo}\prestamos'
            descarga.renombrarReubicar(nombre, 'xlsx', destino)

            datos=[(contador_descargas, campana, nombreAsignado, 1)]
            tablaValidacion.agregarVariosDatos(datos)
        except Exception as e:
            print('isdb_error: ', e)
            datos=[(contador_descargas, campana, nombreAsignado, 0)]
            tablaValidacion.agregarVariosDatos(datos)
            pass

    re_prestamos()
    ultimoRegistro = tablaValidacion.leerDatos()
    descargo = ultimoRegistro[0][3]

    while descargo == 0:
        tablaValidacion.deleteTable(contador_descargas)

        descarga.reiniciar()
        logueo()

        re_prestamos()
        ultimoRegistro = tablaValidacion.leerDatos()
        descargo = ultimoRegistro[0][3]
    else:
        contador_descargas += 1
        print(f"Descargo reporte {grupo} prestamos")
        pass

# ===== 3. Reporte Vacaciones =====
empresa = {
    'bpo': 'BPO PERU S.A.C.'
}
for key, value in empresa.items():
    grupo = key
    razon_social = value

    fecD0 = False
    campana = "planiweb " + grupo

    def re_vacaciones():
        nombreAsignado = f'{grupo}_vacaciones_'
        try:
            descarga.limpia_carpeta_descargas()
            descarga.reporte_vacaciones(razon_social, inicio, fin)
            nombre = descarga.nombreReporte(nombreAsignado, inicio, fin, fecD0)
            destino = descarga.directoryPath + rf'/carga\{grupo}\vacaciones'
            descarga.renombrarReubicar(nombre, 'xlsx', destino)

            origen_vacaciones_pendientes = destino
            destino_vacaciones_pendientes = descarga.directoryPath + rf'/carga\{grupo}\vacaciones_pendientes'
            descarga.copiar_descarga(origen_vacaciones_pendientes, destino_vacaciones_pendientes, currentDate)

            datos=[(contador_descargas, campana, nombreAsignado, 1)]
            tablaValidacion.agregarVariosDatos(datos)
        except Exception as e:
            print('isdb_error: ', e)
            datos=[(contador_descargas, campana, nombreAsignado, 0)]
            tablaValidacion.agregarVariosDatos(datos)
            pass

    re_vacaciones()
    ultimoRegistro = tablaValidacion.leerDatos()
    descargo = ultimoRegistro[0][3]

    while descargo == 0:
        tablaValidacion.deleteTable(contador_descargas)

        descarga.reiniciar()
        logueo()

        re_vacaciones()
        ultimoRegistro = tablaValidacion.leerDatos()
        descargo = ultimoRegistro[0][3]
    else:
        contador_descargas += 1
        print(f"Descargo reporte {grupo} vacaciones")
        pass


# ===== 4. Reporte Personal =====
empresa = {
    'bpo': 'BPO PERU S.A.C.'
}
for key, value in empresa.items():
    grupo = key
    razon_social = value

    fecD0 = False
    campana = "planiweb " + grupo

    def re_perosnal():
        nombreAsignado = f'{grupo}_personal_'
        try:
            descarga.limpia_carpeta_descargas()
            descarga.reporte_personal(razon_social, inicio, fin)
            nombre = descarga.nombreReporte(nombreAsignado, inicio, fin, fecD0)
            destino = descarga.directoryPath + rf'/carga\{grupo}\personal'
            descarga.renombrarReubicar(nombre, 'xlsx', destino)

            datos=[(contador_descargas, campana, nombreAsignado, 1)]
            tablaValidacion.agregarVariosDatos(datos)
        except Exception as e:
            print('isdb_error: ', e)
            datos=[(contador_descargas, campana, nombreAsignado, 0)]
            tablaValidacion.agregarVariosDatos(datos)
            pass

    re_perosnal()
    ultimoRegistro = tablaValidacion.leerDatos()
    descargo = ultimoRegistro[0][3]

    while descargo == 0:
        tablaValidacion.deleteTable(contador_descargas)

        descarga.reiniciar()
        logueo()

        re_perosnal()
        ultimoRegistro = tablaValidacion.leerDatos()
        descargo = ultimoRegistro[0][3]
    else:
        contador_descargas += 1
        print(f"Descargo reporte {grupo} prestamos")
        pass

# ===== 5. Reporte Administrador Acuses =====
empresa = {
    'bpo': 'BPO PERU S.A.C.'
}
for key, value in empresa.items():
    grupo = key
    razon_social = value

    fecD0 = False
    campana = "planiweb " + grupo

    def re_acuses():
        nombreAsignado = f'{grupo}_administrador_acuses_'
        try:
            descarga.limpia_carpeta_descargas()
            descarga.reporte_acuses(razon_social, inicio, fin)
            nombre = descarga.nombreReporte(nombreAsignado, inicio, fin, fecD0)
            destino = descarga.directoryPath + rf'/carga\{grupo}\administrador_acuses'
            descarga.renombrarReubicar(nombre, 'xlsx', destino)

            datos=[(contador_descargas, campana, nombreAsignado, 1)]
            tablaValidacion.agregarVariosDatos(datos)
        except Exception as e:
            print('isdb_error: ', e)
            datos=[(contador_descargas, campana, nombreAsignado, 0)]
            tablaValidacion.agregarVariosDatos(datos)
            pass

    re_acuses()
    ultimoRegistro = tablaValidacion.leerDatos()
    descargo = ultimoRegistro[0][3]

    while descargo == 0:
        tablaValidacion.deleteTable(contador_descargas)

        descarga.reiniciar()
        logueo()

        re_acuses()
        ultimoRegistro = tablaValidacion.leerDatos()
        descargo = ultimoRegistro[0][3]
    else:
        contador_descargas += 1
        print(f"Descargo reporte {grupo} prestamos")
        pass

# ===== 6. Reporte Cesados en Planilla =====
empresa = {
    'bpo': 'BPO PERU S.A.C.'
}
for key, value in empresa.items():
    grupo = key
    razon_social = value

    fecD0 = False
    campana = "planiweb " + grupo

    def re_cesados_planilla():
        nombreAsignado = f'{grupo}_cesados_planilla_'
        try:
            descarga.limpia_carpeta_descargas()
            descarga.reporte_cesados_en_planilla(razon_social, inicio, fin)
            nombre = descarga.nombreReporte(nombreAsignado, inicio, fin, fecD0)
            destino = descarga.directoryPath + rf'/carga\{grupo}\cesados_planilla'
            descarga.renombrarReubicar(nombre, 'xlsx', destino)

            datos=[(contador_descargas, campana, nombreAsignado, 1)]
            tablaValidacion.agregarVariosDatos(datos)
        except Exception as e:
            print('isdb_error: ', e)
            datos=[(contador_descargas, campana, nombreAsignado, 0)]
            tablaValidacion.agregarVariosDatos(datos)
            pass

    re_cesados_planilla()
    ultimoRegistro = tablaValidacion.leerDatos()
    descargo = ultimoRegistro[0][3]

    while descargo == 0:
        tablaValidacion.deleteTable(contador_descargas)

        descarga.reiniciar()
        logueo()

        re_cesados_planilla()
        ultimoRegistro = tablaValidacion.leerDatos()
        descargo = ultimoRegistro[0][3]
    else:
        contador_descargas += 1
        print(f"Descargo reporte {grupo} prestamos")
        pass


print(f"Se descargaron los reportes del día {inicio} al {fin} de la campaña {campana}")
descarga.cerrarSesion()
descarga.gameOver()

# Paso 2: Carga la base de datos al servidor
subprocess.call(['python', './importador/controller.py'])