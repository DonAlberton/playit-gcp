from classifier.models import Priorities
from google.cloud.pubsub_v1 import pubsub_v1
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor


class PubsubPublisherClient(BaseModel):
    project_id: str = "playground-454021"
    publisher: pubsub_v1.SubscriberClient = pubsub_v1.PublisherClient()
    priorities: list[str] = ["low", "medium", "high"]
    topic_name_template: str = ""

    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self, __context) -> None:
        self.topic_name_template = f"projects/{self.project_id}/topics"


    def _create_topic(self, playlist_id: str, priority: str) -> str:
        topic = self.publisher.create_topic(name=f"{self.topic_name_template}/{priority}-{playlist_id}")

        return f"Topic {priority}-{playlist_id} created: {topic}"


    def create_topics(self, playlist_id: str) -> None:
        params = [(playlist_id, priority) for priority in self.priorities]

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._create_topic, *param) for param in params]

            for future in futures:
                print(future.result())


    def _push_message(self, topic_path: str, message: str) -> None:
        self.publisher.publish(topic_path, message.encode("utf-8"))


    def push_queues_messages(self, playlist_id: str, priority_queues: Priorities) -> None:
        for priority, queue in priority_queues:
            if not queue:
                continue

            for message in queue:
                topic_path = f"{self.topic_name_template}/{priority}-{playlist_id}"
                self._push_message(topic_path, message)