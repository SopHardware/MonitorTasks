# main.py
import logging
# import time  # <--- YA NO NECESITAMOS IMPORTAR TIME
from src.database.db_executor import PyODBCExecutor
from src.observers.slack_notifier import SlackNotifier
from src.strategies.submitted_tasks import SubmittedTaskStrategy
from src.strategies.active_processes import ActiveProcessStrategy
from src.core.monitor import TaskMonitorService
from src.utils.config_manager import ConfigManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Función principal para inicializar y ejecutar el servicio de monitoreo.
    Diseñada para ser ejecutada una vez por un programador de tareas.
    """
    logging.info("Iniciando aplicación de monitoreo de tareas Epicor para Programador de Tareas...")

    try:
        # 1. Inicializar el manejador de configuración (Singleton)
        config_manager = ConfigManager()

        # 2. Inicializar el ejecutor de base de datos
        db_executor = PyODBCExecutor()
        logging.info("Executor de base de datos inicializado.")

        # 3. Inicializar los observadores (notificadores)
        slack_notifier = SlackNotifier()
        logging.info("Slack Notifier inicializado.")

        # 4. Inicializar las estrategias de procesamiento de tareas
        strategies = [
            SubmittedTaskStrategy(),
            ActiveProcessStrategy()
        ]
        logging.info(f"Estrategias de tareas cargadas: {[s.category_name for s in strategies]}.")

        # 5. Inicializar el servicio de monitoreo e inyectar dependencias
        task_monitor = TaskMonitorService(db_executor=db_executor, strategies=strategies)
        logging.info("TaskMonitorService inicializado.")

        # 6. Registrar los observadores en el monitor
        task_monitor.add_observer(slack_notifier)
        logging.info("Observadores registrados en el monitor.")

        # *** CAMBIO CLAVE: Ejecutar la lógica de monitoreo una vez ***
        task_monitor.run_monitoring()
        logging.info("Ciclo de monitoreo completado. La aplicación se cerrará.")

        # Ya no necesitamos check_interval_minutes aquí, el Programador de Tareas lo manejará.
        # check_interval_minutes = int(config_manager.get_setting("Monitoring", "check_interval_minutes"))
        # check_interval_seconds = check_interval_minutes * 60
        # logging.info(f"El monitoreo se ejecutará cada {check_interval_minutes} minuto(s).")
        # while True:
        #     task_monitor.run_monitoring()
        #     logging.info(f"Siguiente chequeo en {check_interval_minutes} minuto(s)...")
        #     time.sleep(check_interval_seconds)

    except Exception as e:
        logging.critical(f"Un error crítico ha ocurrido durante la ejecución: {e}", exc_info=True)
        # Considera enviar una notificación de Slack aquí para errores críticos
        # slack_notifier.notify_critical_error(f"Error crítico en el monitoreo: {e}")

if __name__ == "__main__":
    main()