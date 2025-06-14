from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv() # Carga las variables de entorno del archivo .env

class EncryptionUtil:
    """
    Utilidad para cifrar y descifrar cadenas de texto usando Fernet.
    La clave de cifrado se carga desde las variables de entorno.
    """
    _fernet = None

    @classmethod
    def _get_fernet_instance(cls):
        if cls._fernet is None:
            key = os.getenv("ENCRYPTION_KEY")
            if not key:
                raise ValueError("ENCRYPTION_KEY no está configurada en las variables de entorno.")
            try:
                cls._fernet = Fernet(key.encode('utf-8')) # Asegúrate de que la clave esté en bytes
            except Exception as e:
                raise ValueError(f"Clave de cifrado inválida o mal formateada: {e}")
        return cls._fernet

    @classmethod
    def encrypt(cls, data: str) -> bytes:
        """Cifra una cadena de texto."""
        f = cls._get_fernet_instance()
        return f.encrypt(data.encode('utf-8'))

    @classmethod
    def decrypt(cls, encrypted_data: bytes) -> str:
        """Descifra datos en bytes a una cadena de texto."""
        f = cls._get_fernet_instance()
        return f.decrypt(encrypted_data).decode('utf-8')

# Ejemplo de uso (puedes borrarlo una vez que lo entiendas)
# src/utils/encryption.py
# ... (código anterior) ...

if __name__ == "__main__":
    try:
        # ESTA CADENA DEBE SER LA QUE SABES QUE FUNCIONA DIRECTAMENTE CON PYODBC
        # y que probaste en db_executor.py cuando funcionó.
        original_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=GBECDB01;DATABASE=EpicorERP;UID=MonitorTask;PWD=Dxc#2QRm5yuSRK6Ufqh@;"

        print(f"\n--- Original String to Encrypt ---")
        print(f"'{original_string}'") # Imprime con comillas para ver espacios extra
        print(f"Length: {len(original_string)}")

        encrypted_bytes = EncryptionUtil.encrypt(original_string)
        encrypted_string_for_config = encrypted_bytes.decode('utf-8')

        print(f"\n--- Encrypted String for config.ini ---")
        print(f"'{encrypted_string_for_config}'") # Imprime con comillas
        print(f"Length: {len(encrypted_string_for_config)}")
        print("COPIA ESTA CADENA (INCLUYENDO CUALQUIER CARACTER EXTRA SI LO HUBIERA) Y PÉGALA EN config.ini")

        decrypted_string = EncryptionUtil.decrypt(encrypted_string_for_config.encode('utf-8'))
        print(f"\n--- Decrypted String for Verification ---")
        print(f"'{decrypted_string}'") # Imprime con comillas
        print(f"Length: {len(decrypted_string)}")

        assert original_string == decrypted_string
        print("\nVERIFICACIÓN: ¡Cifrado y descifrado de la nueva cadena exitosos dentro de encryption.py!")

    except ValueError as e:
        print(f"Error de configuración: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")