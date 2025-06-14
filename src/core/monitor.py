import logging
from typing import List
from ..core.interfaces import ITaskMonitor, ITaskObserver, IDatabaseExecutor, ITaskProcessingStrategy
from ..models import TaskStatistics, Task
from ..utils.config_manager import ConfigManager # Para obtener límites y umbrales

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TaskMonitorService(ITaskMonitor):
    """
    Servicio principal de monitoreo de tareas.
    Actúa como el Sujeto en el patrón Observador, notificando a los Observadores
    sobre el estado de las tareas.
    Utiliza el patrón de Inyección de Dependencias para el executor de base de datos
    y las estrategias de procesamiento.
    """
    def __init__(self, db_executor: IDatabaseExecutor, strategies: List[ITaskProcessingStrategy]):
        self._observers: List[ITaskObserver] = []
        self._db_executor = db_executor
        self._strategies = strategies
        self._max_tasks_limit = int(ConfigManager().get_setting("Monitoring", "max_tasks_limit"))
        # Puedes añadir un umbral de duración aquí si quieres una alerta específica por tiempo.
        # Por ejemplo, notificar una tarea individual si dura más de 60 minutos,
        # independientemente del número total de tareas.
        # self._long_running_task_threshold_minutes = int(ConfigManager().get_setting("Monitoring", "long_running_task_threshold_minutes"))
        logging.info("TaskMonitorService inicializado con %d estrategias.", len(strategies))


    def add_observer(self, observer: ITaskObserver):
        """Registra un nuevo observador."""
        if observer not in self._observers:
            self._observers.append(observer)
            logging.info(f"Observador '{observer.__class__.__name__}' añadido.")

    def remove_observer(self, observer: ITaskObserver):
        """Elimina un observador registrado."""
        if observer in self._observers:
            self._observers.remove(observer)
            logging.info(f"Observador '{observer.__class__.__name__}' eliminado.")

    def _notify_observers(self, statistics: TaskStatistics):
        """Notifica a todos los observadores sobre nuevas estadísticas."""
        for observer in self._observers:
            try:
                observer.update(statistics)
            except Exception as e:
                logging.error(f"Error al notificar al observador '{observer.__class__.__name__}': {e}")

    def _notify_long_running_task_to_observers(self, task: Task, category: str):
        """Notifica a los observadores sobre una tarea de larga duración individual."""
        for observer in self._observers:
            try:
                observer.notify_long_running_task(task, category)
            except Exception as e:
                logging.error(f"Error al notificar tarea de larga duración al observador '{observer.__class__.__name__}': {e}")

    def run_monitoring(self):
        """
        Ejecuta el ciclo de monitoreo de tareas para cada estrategia.
        """
        logging.info("Iniciando ciclo de monitoreo de tareas...")
        for strategy in self._strategies:
            category_name = strategy.category_name
            logging.info(f"Monitoreando tareas para la categoría: '{category_name}'")
            try:
                query = strategy.get_tasks_query()
                raw_data = self._db_executor.execute_query(query)
                statistics = strategy.process_raw_tasks(raw_data)

                # Notificar siempre sobre las estadísticas (reporte periódico o alerta de límite)
                self._notify_observers(statistics)

                # Opcional: Notificar específicamente si la tarea de mayor duración excede un umbral de tiempo
                # Esto sería una alerta adicional a la del "over_limit"
                # if statistics.longest_running_task and statistics.longest_running_task.duration_minutes is not None:
                #     if statistics.longest_running_task.duration_minutes > self._long_running_task_threshold_minutes:
                #         self._notify_long_running_task_to_observers(
                #             statistics.longest_running_task,
                #             category_name
                #         )
                #         logging.warning(f"Alerta: Tarea de larga duración detectada en '{category_name}': {statistics.longest_running_task.task_description}")

            except Exception as e:
                logging.error(f"Error al procesar la categoría '{category_name}': {e}")
        logging.info("Ciclo de monitoreo de tareas finalizado.")