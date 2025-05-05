from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
from pydantic import BaseModel
import datetime


class TasksClient(BaseModel):
    queue_id: str = ""
    location: str = "europe-central2" # Warsaw
    project_id: str = "playground-454021"
    delay: int = 35
    client: tasks_v2.CloudTasksClient = tasks_v2.CloudTasksClient()
    retry_url: str = ""
    retry_endpoint: str = ""

    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self, __context) -> None:
        self.retry_endpoint = f"{self.retry_url}/start"


    def push_scheduler_reprocessing(self, playlist_id: str, message: str):
        parent = self.client.queue_path(self.project_id, self.location, self.queue_id)

        body: bytes = message.encode()

        scheduled_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=self.delay)
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(scheduled_time)

        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": f"{self.retry_endpoint}/{playlist_id}",
                "headers": {"Content-type": "application/json"},
                "body": body,
            },
            "schedule_time": timestamp
        }

        response = self.client.create_task(parent=parent, task=task)