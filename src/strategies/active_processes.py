from typing import List, Dict, Optional
from datetime import datetime
from ..core.interfaces import ITaskProcessingStrategy
from ..models import Task, TaskStatistics
from ..utils.config_manager import ConfigManager 
import logging

class ActiveProcessStrategy(ITaskProcessingStrategy):
    """
    Estrategia para procesar tareas de la categoría "Proceso Activo".
    """
    @property
    def category_name(self) -> str:
        return "Proceso Activo"

    def get_tasks_query(self) -> str:
        """
        Retorna el query SQL para obtener las tareas "Proceso Activo".
        """
        return """
        SELECT
            t.SysTaskNum,
            t.TaskDescription,
            ISNULL(IIF(prm.ParamCharacter IS NULL, tprm.ParamCharacter, prm.ParamCharacter), '') AS [Function], -- Alias para 'function_id'
            t.TaskType,
            DATEDIFF(MINUTE, DATEADD(HOUR,-6, StartedOn), CURRENT_TIMESTAMP) AS Duracion, -- Alias para 'duration_minutes'
            DATEADD(HOUR,-6, StartedOn) AS StartedOn, -- Alias para 'start_time'
            DATEADD(HOUR, -6, LastActivityOn) AS LastActivityOn,
            t.ProgressPercent,
            sc.SchedDesc,
            t.SubmitUser,
            t.TaskStatus,
            t.ActivityMsg
        FROM ice.SysTask t
        LEFT JOIN Ice.SysAgentSched sc ON t.AgentSchedNum = sc.AgentSchedNum
        LEFT JOIN Ice.SysAgentTaskParam prm ON t.AgentSchedNum = prm.AgentSchedNum AND prm.ParamName = 'FunctionId'
        LEFT JOIN Ice.SysTaskParam tprm ON t.SysTaskNum = tprm.SysTaskNum AND tprm.ParamName = 'FunctionId'
        WHERE TaskStatus = 'ACTIVE'
        ORDER BY t.SysTaskNum
        """

    def process_raw_tasks(self, raw_tasks_data: List[Dict]) -> TaskStatistics:
        """
        Procesa los datos brutos de las tareas y calcula las estadísticas.
        Identifica la tarea con mayor duración.
        """
        tasks: List[Task] = []
        longest_running_task: Optional[Task] = None
        max_tasks_limit = int(ConfigManager().get_setting("Monitoring", "max_tasks_limit"))

        for row in raw_tasks_data:
            try:
                task = Task(
                    task_id=str(row.get('SysTaskNum')),
                    task_description=row.get('TaskDescription'),
                    start_time=row.get('StartedOn'), # Ya viene ajustado en el query
                    submit_user=row.get('SubmitUser'),
                    function_id=row.get('Function'),
                    task_type=row.get('TaskType'),
                    duration_minutes=row.get('Duracion'),
                    last_activity_on=row.get('LastActivityOn'),
                    progress_percent=float(row['ProgressPercent']) if row.get('ProgressPercent') is not None else None,
                    sched_desc=row.get('SchedDesc'),
                    task_status=row.get('TaskStatus'),
                    activity_msg=row.get('ActivityMsg')
                )
                tasks.append(task)

                # Determinar la tarea de mayor duración
                if task.duration_minutes is not None: # Solo si la duración es un valor válido
                    if longest_running_task is None or task.duration_minutes > longest_running_task.duration_minutes:
                        longest_running_task = task
            except Exception as e:
                logging.warning(f"Error al procesar fila de tarea 'Proceso Activo': {row}. Error: {e}")
                continue

        total_tasks = len(tasks)
        over_limit = total_tasks > max_tasks_limit

        return TaskStatistics(
            category_name=self.category_name,
            total_tasks=total_tasks,
            over_limit=over_limit,
            longest_running_task=longest_running_task
        )