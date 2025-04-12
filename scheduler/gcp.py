from google.cloud import firestore, pubsub_v1, tasks_v2
from models import QueueWeights, StartSchedulerRequest
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel
import datetime
from google.protobuf import timestamp_pb2


class PubsubSubscriberClient:
    project_id: str = "playground-454021"
    subscriber: pubsub_v1.SubscriberClient = pubsub_v1.SubscriberClient()
    priorities: list[str] = ["low", "medium", "high"]   
    subscription_name_template: str = f"projects/{project_id}/subscriptions"

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


class FirestoreClient:
    firestore_client: firestore.Client = firestore.Client()
    document_name: str = "queues_weights"
    collection: firestore.Client.collection = firestore_client.collection(document_name)


    def get_queue_weights(self, playlist_id: str) -> QueueWeights:
        doc_ref = self.collection.document(playlist_id)

        doc = doc_ref.get()

        if not doc.exists:
            raise ValueError(f"Playlist id {playlist_id} does not exist")

        return QueueWeights(**doc.to_dict())
    

    def does_playlist_exist(self, playlist_id: str) -> bool:
        doc_ref = self.collection.document(playlist_id) 

        return doc_ref.get().exists


    def create_empty_document(self, playlist_id: str) -> None:
        doc_ref = self.collection.document(playlist_id)
        doc_ref.set({})


    def update_queue_weights(self, playlist_id: str, queue_weights: QueueWeights) -> None:
        doc_ref = self.collection.document(playlist_id)

        doc_ref.set(queue_weights.model_dump())


class TasksClient(BaseModel):
    queue_id: str = "test-task-1"
    location: str = "europe-central2" # Warsaw
    project_id: str = "playground-454021"
    delay: int = 30
    client: tasks_v2.CloudTasksClient = tasks_v2.CloudTasksClient()
    url: str = "http://127.0.0.1:8000/start"

    class Config:
        arbitrary_types_allowed = True

    def push_scheduler_reprocessing(self, message: str):
        parent = self.client.queue_path(self.project_id, self.location, self.queue_id)

        body: bytes = message.encode()

        scheduled_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=self.delay)
        timestamp = timestamp_pb2.Timestamp() 
        timestamp.FromDatetime(scheduled_time)

        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": self.url,
                "headers": {"Content-type": "application/json"},
                "body": body,
            },
            "schedule_time": timestamp 
        }

        response = self.client.create_task(parent=parent, task=task)
        print(f"Task created: {response.name}")


if __name__ == "__main__":
    task_client = TasksClient(queue_id="test-task-queue", url="http://172.104.153.64/")
    task_client.push_scheduler_reprocessing("manialukens")
    # subsciber = PubsubSubscriberClient()

    # weights = {
    #     "high": 3,
    #     "medium": 2,
    #     "low": 1
    # }

    # queue_weights = QueueWeights(**weights)

    # print(subsciber.pull_tracks("0z7gjg85ySD5VXg3bldGt7", queue_weights))

    # pass
    # import time
    # playlist_id = "2elIaOB0fCHjcSABzQpfLD"
    
    # publisher_client = PubsubPublisherClient()
    # subscriber_client = PubsubSubscriberClient()
    # firestore_client = FirestoreClient()

    # print(firestore_client.get_users_priorities(playlist_id))

    # users_priorities = UsersByPriorities(**{"high": ["11180277231"], "low": [], "medium": ["31qvemjqvhkkvdzfmkut24y4lsmy"]})
    # firestore_client.update_users_priorities(playlist_id, users_priorities)

    # print(firestore_client.get_users_priorities(playlist_id))



    # print("Async")
    # start = time.time()
    # publisher_client.create_topics(playlist_id)
    # print(f"Topics creation processing time: {time.time() - start}s")

    # start = time.time()
    # subscriber_client.create_subscriptions(playlist_id)
    # print(f"Subscriber creation processing time: {time.time() - start}s")
    # print("---")

    # priorities = ["low", "medium", "high"]
    # print("Sync")
    # start = time.time()
    # for priority in priorities:
    #     publisher_client._create_topic(playlist_id+"-test", priority)
    # # publisher_client.create_topics(playlist_id)
    # print(f"Topics creation processing time: {time.time() - start}s")

    # start = time.time()
    # # subscriber_client.create_subscriptions(playlist_id)
    # for priority in priorities:
    #     subscriber_client._create_subscription(playlist_id+"-test", priority)
    # print(f"Subscriber creation processing time: {time.time() - start}s")
    # print("---")
