from google.cloud import firestore, pubsub_v1, tasks_v2
from models import QueueWeights, StopSchedulerRequest
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel
import datetime
from google.protobuf import timestamp_pb2


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


class FirestoreClient:
    firestore_client: firestore.Client = firestore.Client()
    document_name: str = "queues_weights"
    collection: firestore.Client.collection = firestore_client.collection(document_name)

    class Config:
        arbitrary_types_allowed = True


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


    def set_taskqueue_readiness(self, playlist_id: str, status: bool) -> None:
        document_name: str = "taskqueue_status"
        collection: firestore.Client.collection = self.firestore_client.collection(document_name)

        doc_ref = collection.document(playlist_id)

        doc_ref.set({"is_ready": status})


    def check_taskqueue_readiness(self, playlist_id: str) -> bool:
        document_name: str = "taskqueue_status"
        collection: firestore.Client.collection = self.firestore_client.collection(document_name)

        doc_ref = collection.document(playlist_id)

        if not doc_ref.get().exists:
            # doc_ref.set({"is_ready": True})
            return False
        
        return doc_ref.get().to_dict()["is_ready"]
       


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



if __name__ == "__main__":
    id = "123-123-123"

    firestore_client = FirestoreClient()
    firestore_client.set_taskqueue_readiness(id, True)


    print(firestore_client.check_taskqueue_readiness(id))

    firestore_client.set_taskqueue_readiness(id, False)

    print(firestore_client.check_taskqueue_readiness(id))
