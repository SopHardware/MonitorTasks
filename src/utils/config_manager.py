import configparser
import os
from .encryption import EncryptionUtil # Importa la utilidad de cifrado

class ConfigManager:
    """
    Gestiona la carga de configuración desde un archivo INI,
    incluyendo el descifrado de la cadena de conexión.
    """
    _instance = None
    _config = None
    _config_path = 'config.ini' # Ruta por defecto, ajusta si es necesario

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._load_config()
        return cls._instance

    @classmethod
    def _load_config(cls):
        cls._config = configparser.ConfigParser()
        if not os.path.exists(cls._config_path):
            raise FileNotFoundError(f"El archivo de configuración '{cls._config_path}' no se encontró.")
        cls._config.read(cls._config_path)

    @classmethod
    def get_setting(cls, section: str, key: str) -> str:
        """
        Obtiene un valor de configuración.
        Si es la cadena de conexión, la descifra.
        """
        if cls._config is None:
            cls._load_config() # Asegura que la configuración esté cargada

        if section not in cls._config:
            raise KeyError(f"Sección '{section}' no encontrada en el archivo de configuración.")
        if key not in cls._config[section]:
            raise KeyError(f"Clave '{key}' no encontrada en la sección '{section}'.")

        value = cls._config[section][key]

        # Si la clave es la cadena de conexión, intenta descifrarla
        if key == "database_connection_string":
            try:
                return EncryptionUtil.decrypt(value.encode('utf-8'))
            except Exception as e:
                raise ValueError(f"No se pudo descifrar la cadena de conexión: {e}")
        return value