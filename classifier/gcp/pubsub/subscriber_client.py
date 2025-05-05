from google.cloud.pubsub_v1 import pubsub_v1
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor


class PubsubSubscriberClient(BaseModel):
    project_id: str = "playground-454021"
    subscriber: pubsub_v1.SubscriberClient = pubsub_v1.SubscriberClient()
    priorities: list[str] = ["low", "medium", "high"]
    subscription_name_template: str = ""
    topic_name_template: str = ""

    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self, __context) -> None:
        self.subscription_name_template = f"projects/{self.project_id}/subscriptions"
        self.topic_name_template = f"projects/{self.project_id}/topics"


    def _create_subscription(self, playlist_id: str, priority: str) -> str:
        subscription = self.subscriber.create_subscription(
            request={
                "name": f"{self.subscription_name_template}/{priority}-{playlist_id}",
                "topic": f"{self.topic_name_template}/{priority}-{playlist_id}"
            }
        )

        return f"Subscription {priority}-{playlist_id} created: {subscription}"


    def create_subscriptions(self, playlist_id: str) -> None:
        params = [(playlist_id, priority) for priority in self.priorities]

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._create_subscription, *param) for param in params]

            for future in futures:
                print(future.result())