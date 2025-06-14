from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    """
    Representa una tarea monitoreada, abarcando campos comunes y específicos
    de ambos tipos de queries ("Mandado a Someter" y "Proceso Activo").
    Los campos que no aplican a ambos queries se marcan como Optional.
    """
    # Campos comunes o variantes similares
    task_id: str                   # Corresponde a AgentSchedNum (Mandado) o SysTaskNum (Proceso Activo)
    task_description: str          # Corresponde a TaskDesc (Mandado) o TaskDescription (Proceso Activo)
    start_time: datetime           # Corresponde a SubmittedOn (Mandado) o StartedOn (Proceso Activo)
    submit_user: str               # Corresponde a SubmitUser en ambos

    # Campos específicos de "Mandado a Someter"
    sched_desc: Optional[str] = None       # SchedDesc
    task_type: Optional[str] = None        # TaskType (también en Proceso Activo, pero con diferente contexto)
    run_procedure: Optional[str] = None    # RunProcedure
    param_maint_program: Optional[str] = None # ParamMaintProgram

    # Campos específicos de "Proceso Activo"
    function_id: Optional[str] = None      # 'Function' (derivado de ParamCharacter/ParamMaintProgram)
    duration_minutes: Optional[int] = None # Duracion (DATEDIFF)
    last_activity_on: Optional[datetime] = None # LastActivityOn
    progress_percent: Optional[float] = None # ProgressPercent
    task_status: Optional[str] = None      # TaskStatus
    activity_msg: Optional[str] = None     # ActivityMsg

    def __str__(self):
        # Una representación amigable para logs o notificaciones
        s = f"ID: {self.task_id}, Descripción: '{self.task_description}', Inicio: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
        if self.task_type:
            s += f", Tipo: {self.task_type}"
        if self.duration_minutes is not None:
            s += f", Duración: {self.duration_minutes} min"
        if self.submit_user:
            s += f", Usuario: {self.submit_user}"
        if self.task_status:
            s += f", Estado: {self.task_status}"
        return s

@dataclass
class TaskStatistics:
    """Contiene las estadísticas y la tarea más antigua para una categoría."""
    category_name: str
    total_tasks: int
    over_limit: bool # Indica si el total_tasks excede el límite configurado (ej. 100)
    longest_running_task: Optional[Task] = None # La tarea con mayor tiempo de ejecución en esta categoría