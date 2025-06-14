import pyodbc
from typing import List, Dict
from ..core.interfaces import IDatabaseExecutor
from ..utils.config_manager import ConfigManager # Para obtener la cadena de conexión
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PyODBCExecutor(IDatabaseExecutor):
    """
    Implementación de IDatabaseExecutor usando pyodbc para conectar a SQL Server.
    Obtiene la cadena de conexión de forma segura a través de ConfigManager.
    """
    def __init__(self):
        self.connection_string = ConfigManager().get_setting("Database", "database_connection_string")
        logging.info("Cadena de conexión de base de datos cargada.")
        #logging.info(f"Cadena de conexión de base de datos cargada: {self.connection_string}") # Descomentar solo para pruebas

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
            # Puedes hacer un manejo de errores más sofisticado aquí
            logging.error(f"Error al conectar a la base de datos (SQLSTATE: {sqlstate}): {ex}")
            raise ConnectionError(f"No se pudo conectar a la base de datos: {ex}") from ex

    def execute_query(self, query: str) -> List[Dict]:
        """
        Ejecuta un query SQL SELECT y devuelve los resultados como una lista de diccionarios.
        Cada diccionario representa una fila y mapea nombres de columna a valores.
        """
        results: List[Dict] = []
        conn = None # Inicializa conn para asegurar que esté definida
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query)

            columns = [column[0] for column in cursor.description] # Obtiene los nombres de las columnas
            logging.debug(f"Query ejecutado: {query[:100]}...") # Loguea solo el inicio del query

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

# Ejemplo de uso (para pruebas, puedes eliminarlo después)
if __name__ == "__main__":
    # NOTA: Para que este ejemplo funcione, necesitas:
    # 1. Tu archivo .env con ENCRYPTION_KEY
    # 2. Tu archivo config.ini con la cadena de conexión cifrada y una URL de Slack
    # 3. Tener el driver ODBC para SQL Server instalado en tu sistema.
    #    (ej. Microsoft ODBC Driver 17 for SQL Server)
    # 4. Asegúrate de que los detalles de la conexión en tu config.ini sean válidos.

    try:
        executor = PyODBCExecutor()

        # Query de prueba simple (asegúrate de que la tabla exista)
        test_query = "SELECT TOP 5 TaskDescription, SysTaskNum FROM Ice.SysTask ORDER BY StartedOn DESC"
        print(f"\n--- Ejecutando query de prueba ---")
        data = executor.execute_query(test_query)

        if data:
            print("Resultados del query de prueba:")
            for row in data:
                print(row)
        else:
            print("No se encontraron resultados para el query de prueba.")

        # Prueba con un query inválido para ver el manejo de errores
        # print("\n--- Probando manejo de errores con query inválido ---")
        # executor.execute_query("SELECT * FROM NonExistentTable")

    except (ConnectionError, RuntimeError, ValueError) as e:
        print(f"Error en la aplicación de consola: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")