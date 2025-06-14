# 🚀 Monitoreo de Tareas Epicor: ¡Mantén tus Procesos Bajo Control\! 🚀

-----

## 👋 ¡Bienvenido al Monitoreo Inteligente para Epicor\!

¿Cansado de que los procesos de fondo en Epicor se descontrolen? ¿Te gustaría saber al instante cuando una tarea lleva demasiado tiempo ejecutándose o cuando hay un cuello de botella de procesos pendientes? ¡Esta herramienta es para ti\!

El **Monitoreo de Tareas Epicor** es una aplicación en Python diseñada para vigilar tus tareas de fondo en tiempo real y enviarte **alertas claras directamente a Slack**. Así, tú y tu equipo pueden reaccionar rápidamente y mantener Epicor funcionando sin problemas.

-----

## ✨ ¿Qué Puede Hacer por Ti?

  * **Visibilidad Total:** Obtén una instantánea clara de tus tareas "Mandado a Someter" y "Proceso Activo".
  * **Alertas Inteligentes:**
      * **Límites de Tareas:** Recibe una alerta si la cantidad de tareas activas supera un límite que tú defines. ¡Evita cuellos de botella antes de que causen problemas\!
      * **Detecta Tareas Lentas:** Identifica y notifica si una tarea individual está tardando más de lo esperado.
  * **Notificaciones Instantáneas:** Todas las alertas llegan directamente a tu canal de Slack favorito, con mensajes fáciles de entender y visualmente atractivos.
  * **Configuración Segura:** Tu información sensible (como las credenciales de la base de datos) se **cifra automáticamente**, manteniéndola protegida.
  * **Fácil de Extender:** ¿Necesitas monitorear un nuevo tipo de tarea o enviar alertas por correo electrónico? ¡Gracias a su diseño modular, es pan comido\!

-----

## 🛠️ ¡Manos a la Obra\! Configuración Rápida

Para poner en marcha tu monitor, necesitarás algunos preparativos y una configuración sencilla.

### Requisitos

  * **Python 3.8 o superior.**
  * **Driver ODBC para SQL Server:** Asegúrate de tener instalado el driver de Microsoft adecuado (ej. "ODBC Driver 17" o "18") en la máquina donde ejecutarás la app.
  * **Acceso a tu DB Epicor:** Un usuario de SQL Server con permisos de `SELECT` en las tablas `Ice.SysTask`, `Ice.SysAgentSched`, y `Ice.SysAgentTaskParam`.
  * **Webhook de Slack:** Una URL de [Webhook entrante de Slack](https://api.slack.com/messaging/webhooks) para que la app pueda enviar tus notificaciones.

### Instalación en 3 Pasos

1.  **Clona el proyecto:**

    ```bash
    git clone https://github.com/SopHardware/MonitorTasks
    cd tu-repositorio-monitoreo
    ```

    *(No olvides reemplazar `tu-usuario/tu-repositorio.git` con la dirección real de tu repo)*

2.  **Crea y activa tu entorno virtual:**

    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instala las dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

### ¡A Configurar\!

1.  **Tu Clave Secreta (`.env`):**
    Primero, generaremos una clave de cifrado. Ejecuta esto una vez:

    ```python
    from cryptography.fernet import Fernet
    key = Fernet.generate_key().decode()
    print(key)
    ```

    Copia la clave que te muestre. Luego, crea un archivo llamado **`.env`** en la raíz de tu proyecto y pega la clave así:

    ```
    ENCRYPTION_KEY=tu_clave_fernet_generada_aqui
    ```

2.  **El Cerebro de la Configuración (`config.ini`):**
    Este archivo, también en la raíz, contendrá tus ajustes. Necesitarás tu **cadena de conexión a la base de datos cifrada** y la **URL de tu Webhook de Slack**.

      * **Para cifrar tu cadena de conexión:**

          * Abre `src/utils/encryption.py`.
          * Busca la línea `original_string = "..."` dentro del bloque `if __name__ == "__main__":` y reemplázala con tu cadena de conexión SQL Server real (ej. `DRIVER={ODBC Driver 17 for SQL Server};SERVER=tu_servidor;DATABASE=tu_db;UID=tu_usuario;PWD=tu_pwd;`).
          * Ejecuta `python -m src.utils.encryption`.
          * Copia la cadena que aparece como "Encrypted String for config.ini".

      * Ahora, edita o crea tu **`config.ini`** así:

        ```ini
        [Database]
        database_connection_string=<PEGAR_AQUI_TU_CADENA_CIFRADA>

        [Slack]
        webhook_url=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
        ; ^^^ ¡IMPORTANTE! Reemplaza con tu URL de webhook real de Slack ^^^

        [Monitoring]
        max_tasks_limit = 100
        check_interval_minutes = 5
        ; long_running_task_threshold_minutes = 60
        ; ^^^ Opcional: Si quieres una alerta específica por duración de tarea (descomentar si se usa en monitor.py) ^^^
        ```

-----

## 🏃 ¡A Correr\!

Esta aplicación está diseñada para ejecutarse periódicamente, ¡idealmente con el **Programador de Tareas de Windows**\! De esa forma, puedes configurarla para que chequee tus procesos cada X minutos sin tener que preocuparte.

### Configuración en el Programador de Tareas de Windows

1.  Abre el **Programador de Tareas** (búscalo en el menú de inicio).
2.  Haz clic en **"Crear tarea..."** en el panel de acciones (te da más control que la "tarea básica").
3.  **Pestaña General:** Ponle un nombre fácil de recordar, como `Monitor de Tareas Epicor`.
4.  **Pestaña Desencadenadores:**
      * Haz clic en **"Nuevo..."**.
      * Configura que la tarea se repita, por ejemplo, **`cada 5 minutos`** (o el valor de `check_interval_minutes` en tu `config.ini`).
      * Selecciona `Indefinidamente` como duración.
5.  **Pestaña Acciones:** ¡Aquí es donde le decimos qué ejecutar\!
      * Haz clic en **"Nuevo..."**.
      * **Acción:** `Iniciar un programa`.
      * **Programa o script:** La ruta **completa** al `python.exe` dentro de tu entorno virtual.
          * Ejemplo: `C:\Users\TuUsuario\tu_app_monitoreo\venv\Scripts\python.exe`
      * **Agregar argumentos (opcional):** `main.py`
      * **Iniciar en (opcional):** La ruta **completa** a la carpeta raíz de tu proyecto (donde está `main.py` y `config.ini`).
          * Ejemplo: `C:\Users\TuUsuario\tu_app_monitoreo`
      * Haz clic en **"Aceptar"**.
6.  **Pestaña Configuración:**
      * Te sugiero marcar `Detener la tarea si se ejecuta durante más de` (ej., 30 minutos) para evitar que se quede "colgada".
      * También, selecciona `No iniciar una nueva instancia` si la tarea ya se está ejecutando, para evitar duplicados.
7.  Haz clic en **"Aceptar"** y proporciona las credenciales de un usuario del sistema que tenga permiso para ejecutar scripts y acceder a la red (si tu DB no está en la misma máquina).

-----

## 💡 ¿Quieres Más? ¡Extiende el Monitor\!

Gracias a su diseño modular, añadir nuevas funcionalidades es sencillo:

  * **¡Más Categorías de Monitoreo\!** ¿Hay otro tipo de tarea Epicor que te interese vigilar? Crea una nueva "estrategia" (una clase que implemente `ITaskProcessingStrategy`) en `src/strategies/` y añádela a la lista en `main.py`. ¡Así de fácil\!
  * **¡Más Formas de Notificar\!** ¿Prefieres alertas por correo electrónico o Microsoft Teams? Crea un nuevo "observador" (una clase que implemente `ITaskObserver`) en `src/observers/` y regístralo en `main.py`.

## 🤝 ¡Colabora\!

¿Tienes ideas para mejorar el monitor? ¿Encontraste un error? ¡Tu ayuda es bienvenida\!
No dudes en abrir un *issue* o enviar un *pull request*.

## 📄 Licencia

Este proyecto está liberado bajo la **Licencia MIT**. Consulta el archivo `LICENSE` para más detalles.

-----
