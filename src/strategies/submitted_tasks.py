from typing import List, Dict, Optional
from datetime import datetime
from ..core.interfaces import ITaskProcessingStrategy
from ..models import Task, TaskStatistics
from ..utils.config_manager import ConfigManager #
import logging 

class SubmittedTaskStrategy(ITaskProcessingStrategy):
    """
    Estrategia para procesar tareas de la categoría "Mandado a Someter".
    """
    @property
    def category_name(self) -> str:
        return "Mandado a Someter"

    def get_tasks_query(self) -> str:
        """
        Retorna el query SQL para obtener las tareas "Mandado a Someter".
        """
        return """
        SELECT
            t.AgentSchedNum,
            s.SchedDesc,
            t.TaskDesc,
            t.TaskType,
            t.RunProcedure,
            DATEADD(HOUR,-6, SubmittedOn) AS SubmittedOn, -- Alias para mapear a 'start_time'
            t.SubmitUser,
            t.ParamMaintProgram
        FROM ice.SysAgentTask t
        LEFT JOIN Ice.SysAgentSched s ON t.AgentID = s.AgentID AND t.AgentSchedNum = s.AgentSchedNum
        WHERE s.SchedDesc = 'Immediate Run Request'
        ORDER BY t.AgentSchedNum
        """

    def process_raw_tasks(self, raw_tasks_data: List[Dict]) -> TaskStatistics:
        """
        Procesa los datos brutos de las tareas y calcula las estadísticas.
        Identifica la tarea más antigua basada en 'SubmittedOn'.
        """
        tasks: List[Task] = []
        longest_running_task: Optional[Task] = None
        max_tasks_limit = int(ConfigManager().get_setting("Monitoring", "max_tasks_limit"))

        # Convertir los datos brutos del diccionario a objetos Task
        for row in raw_tasks_data:
            try:
                # Mapeo cuidadoso de columnas a atributos de Task
                task = Task(
                    task_id=str(row.get('AgentSchedNum')),
                    task_description=row.get('TaskDesc'),
                    start_time=row.get('SubmittedOn'), # Ya viene ajustado en el query
                    submit_user=row.get('SubmitUser'),
                    sched_desc=row.get('SchedDesc'),
                    task_type=row.get('TaskType'),
                    run_procedure=row.get('RunProcedure'),
                    param_maint_program=row.get('ParamMaintProgram')
                    # Otros campos de Task se dejarán como None por defecto
                )
                tasks.append(task)

                # Determinar la tarea más antigua (tiempo de inicio más temprano)
                if longest_running_task is None or task.start_time < longest_running_task.start_time:
                    longest_running_task = task
            except Exception as e:
                logging.warning(f"Error al procesar fila de tarea 'Mandado a Someter': {row}. Error: {e}")
                continue

        total_tasks = len(tasks)
        over_limit = total_tasks > max_tasks_limit

        return TaskStatistics(
            category_name=self.category_name,
            total_tasks=total_tasks,
            over_limit=over_limit,
            longest_running_task=longest_running_task
        )