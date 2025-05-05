from scheduler.models.queue_weights import QueueWeights
from google.cloud.pubsub_v1 import pubsub_v1
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor


class PubsubSubscriberClient(BaseModel):
    project_id: str = "playground-454021"
    subscriber: pubsub_v1.SubscriberClient = pubsub_v1.SubscriberClient()
    priorities: list[str] = ["low", "medium", "high"]
    subscription_name_template: str = f"projects/{project_id}/subscriptions"

    class Config:
        arbitrary_types_allowed = True


    def _pull_subscription_tracks(self, subscription_path: str, weight: int) -> list[str]:
        response = self.subscriber.pull(
            request={
                "subscription": subscription_path,
                "max_messages": weight,
                "return_immediately": True
            }
        )

        if not response.received_messages:
            return []

        acks_ids: str = []
        output: str = []
        for received_message in response.received_messages:
            acks_ids.append(received_message.ack_id)
            output.append(received_message.message.data.decode())

        self.subscriber.acknowledge(
            {
                "subscription": subscription_path,
                "ack_ids": acks_ids
            }
        )

        return output


    def pull_tracks(self, playlist_id: str, queue_weights: QueueWeights) -> list[str]:
        futures = []

        with ThreadPoolExecutor() as executor:
            for priority, weight in queue_weights.model_dump().items():
                subscription_path = f"{self.subscription_name_template}/{priority}-{playlist_id}"
                futures.append(executor.submit(self._pull_subscription_tracks, *(subscription_path, weight)))

        results: list[list[str]] = []
        for future in futures:
            results.append(future.result())

        return [item for sublist in results for item in sublist]