from abc import ABC, abstractmethod
from typing import List, Optional
from ..models import Task, TaskStatistics

# --- Interfaces para el monitoreo y notificación (Patrón Observador) ---

class ITaskObserver(ABC):
    """
    Interfaz para un observador que reacciona a los eventos del monitoreo de tareas.
    """
    @abstractmethod
    def update(self, statistics: TaskStatistics):
        """
        Método llamado por el sujeto para notificar al observador sobre nuevas estadísticas.
        """
        pass

    @abstractmethod
    def notify_long_running_task(self, task: Task, category: str):
        """
        Método llamado para notificar sobre una tarea que lleva mucho tiempo ejecutándose.
        """
        pass

class ITaskMonitor(ABC):
    """
    Interfaz para el Sujeto (monitor de tareas) que observa el estado de las tareas.
    """
    @abstractmethod
    def add_observer(self, observer: ITaskObserver):
        """Registra un nuevo observador."""
        pass

    @abstractmethod
    def remove_observer(self, observer: ITaskObserver):
        """Elimina un observador registrado."""
        pass

    @abstractmethod
    def run_monitoring(self):
        """Ejecuta el ciclo de monitoreo de tareas."""
        pass

# --- Interfaces para la ejecución de queries (Inyección de Dependencias) ---

class IDatabaseExecutor(ABC):
    """
    Interfaz para la ejecución de queries SQL contra una base de datos.
    """
    @abstractmethod
    def execute_query(self, query: str) -> List[dict]:
        """
        Ejecuta un query SQL SELECT y devuelve una lista de diccionarios.
        Cada diccionario representa una fila y mapea nombres de columna a valores.
        """
        pass

# --- Interfaces para las estrategias de procesamiento de tareas (Patrón Estrategia) ---

class ITaskProcessingStrategy(ABC):
    """
    Interfaz para una estrategia que define cómo procesar un tipo específico de tarea.
    """
    @property
    @abstractmethod
    def category_name(self) -> str:
        """Retorna el nombre de la categoría de tareas que maneja esta estrategia."""
        pass

    @abstractmethod
    def get_tasks_query(self) -> str:
        """
        Retorna el query SQL específico para obtener las tareas de esta categoría.
        """
        pass

    @abstractmethod
    def process_raw_tasks(self, raw_tasks_data: List[dict]) -> TaskStatistics:
        """
        Procesa los datos brutos de las tareas obtenidas de la base de datos
        y calcula las estadísticas para esta categoría.
        """
        pass