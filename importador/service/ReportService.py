import pandas as pd
import pymysql
import json
from datetime import datetime
import os
import re

class ReportService:
    def loadData(self,filePath, tableName : str, dbName : str, tipo, fecha_insert, anio_insert, periodo_insert, columnas_id, grupo, code, skip_rows, properties : {}, renameColumns : {}, converters : []):
        filePath = filePath
        
        # Nombre de la tabla
        dbTable = tableName

        percentage = {}
        for convert in converters:
            percentage[convert] = self.convertToPercentage
        
        # Lee el archivo EXCEL con pandas
        #df = pd.read_excel( filePath,  sheet_name=0, engine='openpyxl', skiprows=0, dtype=properties, converters=percentage)
        if tipo == 'csv':
            df = pd.read_csv(filePath, sep='|', dtype=str, header=0, encoding='ISO-8859-1')
        elif tipo == 'excel':
            if code == "vacaciones":
                df1 = pd.read_excel(filePath, dtype=str, skiprows=9)
                df2 = pd.read_excel(filePath, dtype=str, skiprows=10)

                df1_cols = df1.columns
                df2_cols = df2.columns
                anios = [elemento for elemento in df1_cols if len(elemento) == 4 and elemento[:2] == '20']
                names = df1_cols[:9].append(df2_cols[9:17])

                no_existe_df = True
                for i in range(len(anios)):
                    if no_existe_df:
                        df = df2.iloc[:, :9].join(df2.iloc[:, 9 + (8*i):17 +(8*i)])
                        mapeo_nombres = dict(zip(df.columns, names))
                        df.rename(columns=mapeo_nombres, inplace=True)
                        df.insert(0, "anio", anios[i])

                        no_existe_df = False
                    else:
                        df_x = df2.iloc[:, :9].join(df2.iloc[:, 9 + (8*i):17 +(8*i)])
                        mapeo_nombres = dict(zip(df_x.columns, names))
                        df_x.rename(columns=mapeo_nombres, inplace=True)
                        df_x.insert(0, "anio", anios[i])

                        df = pd.concat([df, df_x], axis=0)
            elif code == "vacaciones_pendientes":
                df1 = pd.read_excel(filePath, dtype=str, skiprows=9)
                df2 = pd.read_excel(filePath, dtype=str, skiprows=10)

                df1_cols = df1.columns
                df2_cols = df2.columns
                names = df1_cols[:9].append(df2_cols[-7:-2]).append(df1_cols[-2:])
                df = df2.iloc[:, :9].join(df2.iloc[:, -7:])
                mapeo_nombres = dict(zip(df.columns, names))
                df.rename(columns=mapeo_nombres, inplace=True)
            elif code == "gastos_planilla":
                df1 = pd.read_excel(filePath, dtype=str, skiprows=10)
                df1.columns.values[0] = 'concepto_costo'
                df1.columns.values[-4] = 'TOTAL OPERATIVOS'
                df1.columns.values[-2] = 'TOTAL STAFF'
                df1.columns.values[-1] = 'TOTAL'

                conceptos = ['REMUNERACIONES', 'COMISIONES', 'CARGA LABORAL', 'PRESTACION ALIMENTARIA','MOVILIDAD','TOTALES']

                lista = []
                i = 1
                for valor in df1['concepto_costo']:
                    if valor == conceptos[i]:
                        concepto = conceptos[i]
                        i+=1
                    else:
                        concepto = conceptos[i-1]
                    lista.append((concepto, valor))

                df_x = pd.DataFrame(lista, columns=['concepto', 'concepto_detalle'])

                columnas = []
                for value in df1.columns:
                    columnas.append(value)

                no_existe_df = True
                
                for i in range(1,len(columnas)):
                    centro_costo = columnas[i]

                    lista2 = []
                    for valor in df1[centro_costo]:
                        lista2.append((centro_costo, valor))

                    df_y = pd.DataFrame(lista2, columns=['centro_costo', 'gasto'])
                    df_t = pd.concat([df_x, df_y], axis=1)
                
                    if no_existe_df:
                        df = df_t.copy()
                        no_existe_df = False
                    else:
                        df = pd.concat([df, df_t])
            else:
                df = pd.read_excel(filePath, dtype=str, skiprows=skip_rows)

        if fecha_insert:
            df.insert(0, 'fecha', fecha_insert)
        if anio_insert:
            df.insert(0, 'anio', anio_insert)
        if periodo_insert:
            df.insert(0, 'periodo', periodo_insert)

        # Renombrar la columna        
        df.columns = df.columns.str.strip()
        df.rename(columns=renameColumns, inplace=True)

        # Formatear las columnas
        df = df.fillna(value='')
        df.columns = df.columns.str.lower()
        df.columns = df.columns.str.replace(r'^\d+\.-\s*', '', regex=True)
        df.columns = df.columns.str.replace('\n', '')
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace(' ', '_')
        df.columns = df.columns.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
        df.columns = df.columns.str.lstrip('_')

        def limpiar_encabezados(encabezado):
            return re.sub(r'\W+', '_', encabezado)
        #Limpia  2 o mas"_" seguidos, "_" del final del texto y limita a 35 caracteres
        def underscores(text):
            text = re.sub(r"\_+", "_", text)
            text = text.rstrip("_")
            text = text[:35]
            return text
        df.columns = df.columns.map(limpiar_encabezados)
        df.columns = df.columns.map(underscores)

        if  columnas_id:
            id_df = df[columnas_id].astype(str).apply(lambda x: ''.join(x), axis=1)
            df.insert(0, "id", id_df)

            def limpiar_columna(texto):
                texto_limpio = texto.replace(" ", "").replace("/", "").replace(":", "")
                return texto_limpio

            df['id'] = df['id'].apply(limpiar_columna)
        
        if grupo:
            df['grupo'] = grupo

        """
        print(df.columns)
        for i in df.columns:
            print(i)
        #print(df)
        exit() #"""
        # Configurar la conexión a la base de datos
        properties = self.getProperties()
        conn = pymysql.connect(
            host=properties['DB_HOST'],
            database= dbName,
            user=properties['DB_USER'],
            password=properties['DB_PASSWORD'],
            port=3306
        )

        if (code == "vacaciones") | (code == "vacaciones_pendientes") | (code == "personal") | (code == "cesados_planilla"):
            cur = conn.cursor()
            cur.execute("START TRANSACTION;")
            sqlHeading = "`"+"`,`".join(df.columns)+"`"
            chunks = [df[i:i + 200] for i in range(0, df.shape[0], 200)]
            for chunk in chunks:
                values = [tuple(row) for _, row in chunk.iterrows()]
                try:
                    consulta = f"""INSERT INTO {dbTable} ({sqlHeading}) VALUES ({', '.join(['%s'] * len(df.columns))})
                                    ON DUPLICATE KEY UPDATE {', '.join([f"{col} = VALUES({col})" for col in df.columns])};"""
                    cur.executemany(consulta, values)
                    conn.commit()
                except Exception as e:
                    print("Ocurrió un error:", e)
            print('Se ejecuto correctamente la consulta: ' + dbName + " / " + grupo + " / " + tableName)
        else:
            try:
                # Crear un cursor y comenzar una transacción
                cur = conn.cursor()
                cur.execute("START TRANSACTION;")
                #cur.execute(f"TRUNCATE TABLE {dbTable};")
                
                sqlHeading = "`"+"`,`".join(df.columns)+"`"
                
                chunks = [df[i:i + 200] for i in range(0, df.shape[0], 200)]

                #elimina registros para ser reemplazados
                if anio_insert:
                    cur.execute(f"delete from {dbTable} where anio = {anio_insert} and grupo = '{grupo}';")

                for chunk in chunks:
                    values = [tuple(row) for _, row in chunk.iterrows()]
                    try:
                        # Ejecutar el comando INSERT INTO para cada grupo de 50 filas
                        consulta = f"""INSERT INTO {dbTable} ({sqlHeading}) VALUES ({', '.join(['%s'] * len(df.columns))});"""
                        cur.executemany(consulta, values)
                        conn.commit()
                        #print(f"Se insertaron con éxito {len(chunk)} filas")
                    except Exception as e:
                        print("Ocurrió un error:", e)
                                
                print('Se ejecuto correctamente la consulta: ' + dbName + " / " + grupo + " / " + tableName)

            except Exception as e:
                # Revertir la transacción si hay un error            
                conn.rollback()    
                print("Hubo un error al importar la informacion: " + str(e) )
                return 400 
                
            finally:
                # Cerrar la conexión a la base de datos
                cur.close()
                conn.close()

            return 200
    
    def getProperties(self):
        config_data = None
        with open('./importador/config.json') as config_file:
            config_data = json.load(config_file)

        return config_data
    
    def convertToPercentage(self,x):
        return "{:.2f}%".format(x * 100)
