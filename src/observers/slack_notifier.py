import requests
import json
import logging
from typing import Optional
from ..core.interfaces import ITaskObserver
from ..models import Task, TaskStatistics
from ..utils.config_manager import ConfigManager # Para obtener la URL del webhook

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SlackNotifier(ITaskObserver):
    """
    Implementación de ITaskObserver que envía notificaciones a un canal de Slack
    usando un webhook.
    """
    def __init__(self):
        self.webhook_url = ConfigManager().get_setting("Slack", "webhook_url")
        if not self.webhook_url:
            logging.warning("URL de webhook de Slack no configurada. Las notificaciones a Slack no funcionarán.")
        logging.info("Slack Notifier inicializado.")

    def _send_slack_message(self, message: str, title: Optional[str] = None):
        """
        Método interno para enviar un mensaje JSON al webhook de Slack.
        """
        if not self.webhook_url:
            logging.error("No se puede enviar el mensaje a Slack: URL de webhook no configurada.")
            return

        payload = {
            "text": title if title else message,
            "attachments": [
                {
                    "text": message,
                    "color": "#36a64f" # Color verde por defecto para mensajes informativos
                }
            ]
        }

        try:
            response = requests.post(self.webhook_url, data=json.dumps(payload),
                                     headers={'Content-Type': 'application/json'})
            response.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)
            logging.info(f"Mensaje enviado a Slack con éxito. Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al enviar mensaje a Slack: {e}. Respuesta: {getattr(e.response, 'text', 'N/A')}")
        except Exception as e:
            logging.error(f"Error inesperado al preparar/enviar mensaje a Slack: {e}")

    def update(self, statistics: TaskStatistics):
        """
        Notifica al observador con las estadísticas de tareas.
        Se usa para reportes periódicos y para notificar sobre exceso de límite.
        """
        message_parts = [
            f"📊 *Reporte de Tareas - {statistics.category_name}* 📊",
            f"Total de tareas en ejecución: `{statistics.total_tasks}`"
        ]

        if statistics.over_limit:
            message_parts.append(f"🚨 ¡ADVERTENCIA! El límite de {ConfigManager().get_setting('Monitoring', 'max_tasks_limit')} tareas ha sido *EXCEDIDO*.")
            title = f"🚨 ALERTA: Límite de Tareas Excedido - {statistics.category_name}"
            color = "#FF0000" # Rojo para advertencias
        else:
            title = f"Reporte Diario de Tareas - {statistics.category_name}"
            color = "#36a64f"

        if statistics.longest_running_task:
            message_parts.append(f"⏳ Tarea de mayor duración: \n```{str(statistics.longest_running_task)}```")
            if not statistics.over_limit: # Si no hay alerta de límite, pero sí de duración
                 color = "#FFA500" # Naranja para advertencias de duración

        full_message = "\n".join(message_parts)

        # Ajusta el color del attachment
        payload = {
            "text": title, # El título se muestra como texto principal en algunas vistas de Slack
            "attachments": [
                {
                    "text": full_message,
                    "color": color
                }
            ]
        }
        if not self.webhook_url: # En este caso, ya no usamos _send_slack_message directamente
            logging.error("No se puede enviar el mensaje a Slack: URL de webhook no configurada.")
            return

        try:
            response = requests.post(self.webhook_url, data=json.dumps(payload),
                                     headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            logging.info(f"Reporte/Alerta enviado a Slack con éxito. Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al enviar reporte/alerta a Slack: {e}. Respuesta: {getattr(e.response, 'text', 'N/A')}")
        except Exception as e:
            logging.error(f"Error inesperado al preparar/enviar reporte/alerta a Slack: {e}")


    def notify_long_running_task(self, task: Task, category: str):
        """
        Notifica específicamente sobre una tarea individual que lleva mucho tiempo.
        Este método se podría usar para notificaciones inmediatas si la tarea supera un umbral
        de tiempo predefinido, independientemente del límite de 100 tareas.
        """
        title = f"⏰ ALERTA: Tarea de Larga Duración Detectada ({category})"
        message = (
            f"La siguiente tarea está en ejecución por un tiempo excesivo:\n"
            f"```\n{str(task)}\n```"
            f"\nPor favor, investiga esta tarea."
        )
        self._send_slack_message(message, title=title)


# Ejemplo de uso (para pruebas, puedes eliminarlo después)
if __name__ == "__main__":
    # NOTA: Para que este ejemplo funcione, necesitas:
    # 1. Tu archivo .env con ENCRYPTION_KEY
    # 2. Tu archivo config.ini con una URL de webhook de Slack VÁLIDA
    #    (No la ciframos porque no es información tan crítica como credenciales de DB)

    try:
        notifier = SlackNotifier()

        # Prueba de notificación de reporte (como un update)
        from datetime import datetime, timedelta
        dummy_task_long = Task(
            task_id="TASK123",
            task_description="Proceso de Cierre Mensual",
            start_time=datetime.now() - timedelta(hours=3, minutes=45),
            submit_user="AdminUser",
            duration_minutes=225,
            task_status="ACTIVE"
        )
        stats_over_limit = TaskStatistics(
            category_name="Proceso Activo",
            total_tasks=105,
            over_limit=True,
            longest_running_task=dummy_task_long
        )
        print("\n--- Enviando reporte de tareas (límite excedido y tarea larga) ---")
        notifier.update(stats_over_limit)

        # Prueba de notificación de tarea de larga duración individual
        dummy_task_specific = Task(
            task_id="TASK456",
            task_description="Generación de Informe Diario",
            start_time=datetime.now() - timedelta(minutes=65),
            submit_user="ReportUser",
            duration_minutes=65
        )
        print("\n--- Enviando alerta de tarea de larga duración específica ---")
        notifier.notify_long_running_task(dummy_task_specific, "Mandado a Someter")

        # Prueba de reporte normal
        stats_normal = TaskStatistics(
            category_name="Mandado a Someter",
            total_tasks=50,
            over_limit=False
        )
        print("\n--- Enviando reporte de tareas normal ---")
        notifier.update(stats_normal)


    except Exception as e:
        print(f"Ocurrió un error al probar SlackNotifier: {e}")