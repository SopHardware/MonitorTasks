import pyodbc
from typing import List, Dict
from ..core.interfaces import IDatabaseExecutor
# from ..utils.config_manager import ConfigManager # <--- COMENTA O ELIMINA ESTA LÍNEA
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PyODBCExecutor(IDatabaseExecutor):
    """
    Implementación de IDatabaseExecutor usando pyodbc para conectar a SQL Server.
    *** USANDO CADENA DE CONEXIÓN DIRECTA PARA PRUEBAS (SIN CIFRADO) ***
    """
    def __init__(self):
        # *** REEMPLAZA ESTA CADENA CON LA MISMA QUE USAS EN SSMS Y QUE FUNCIONA ***
        # Asegúrate que sea la cadena COMPLETA con DRIVER, SERVER, DATABASE, UID, PWD
        self.connection_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=GBECDB01;DATABASE=EpicorERP;UID=MonitorTask;PWD=Dxc#2QRm5yuSRK6Ufqh@;"
        logging.info(f"Cadena de conexión directa cargada para prueba: {self.connection_string}")

    def _get_connection(self):
        """
        Establece y retorna una nueva conexión a la base de datos.
        """
        try:
            conn = pyodbc.connect(self.connection_string)
            logging.debug("Conexión a la base de datos establecida.")
            return conn
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            logging.error(f"Error al conectar a la base de datos (SQLSTATE: {sqlstate}): {ex}")
            raise ConnectionError(f"No se pudo conectar a la base de datos: {ex}") from ex

    def execute_query(self, query: str) -> List[Dict]:
        """
        Ejecuta un query SQL SELECT y devuelve los resultados como una lista de diccionarios.
        Cada diccionario representa una fila y mapea nombres de columna a valores.
        """
        results: List[Dict] = []
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query)

            columns = [column[0] for column in cursor.description]
            logging.debug(f"Query ejecutado: {query[:100]}...")

            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            logging.debug(f"Query ejecutado exitosamente. Se encontraron {len(results)} filas.")
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            logging.error(f"Error al ejecutar query (SQLSTATE: {sqlstate}): {ex} - Query: {query}")
            raise RuntimeError(f"Error al ejecutar el query: {ex}") from ex
        except Exception as e:
            logging.error(f"Error inesperado al ejecutar query: {e} - Query: {query}")
            raise e
        finally:
            if conn:
                conn.close()
                logging.debug("Conexión a la base de datos cerrada.")
        return results

# El bloque if __name__ == "__main__": permanece igual para probar.
if __name__ == "__main__":
    try:
        executor = PyODBCExecutor()

        test_query = "SELECT TOP 5 TaskDescription, SysTaskNum FROM Ice.SysTask ORDER BY StartedOn DESC"
        print(f"\n--- Ejecutando query de prueba ---")
        data = executor.execute_query(test_query)

        if data:
            print("Resultados del query de prueba:")
            for row in data:
                print(row)
        else:
            print("No se encontraron resultados para el query de prueba.")

    except (ConnectionError, RuntimeError, ValueError) as e:
        print(f"Error en la aplicación de consola: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")