from google.cloud import pubsub_v1, firestore, tasks_v2
from concurrent.futures import ThreadPoolExecutor
from models import UsersByPriorities, Priorities
from pydantic import BaseModel
import datetime
from google.protobuf import timestamp_pb2


class PubsubSubscriberClient(BaseModel):
    project_id: str = "playground-454021"
    subscriber: pubsub_v1.SubscriberClient = pubsub_v1.SubscriberClient()
    priorities: list[str] = ["low", "medium", "high"]   
    subscription_name_template: str = ""
    topic_name_template: str = ""

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

    
class FirestoreClient:
    firestore_client: firestore.Client = firestore.Client()
    document_name: str = "users_priorities"
    collection: firestore.Client.collection = firestore_client.collection(document_name)


    def get_users_priorities(self, playlist_id: str) -> UsersByPriorities:
        doc_ref = self.collection.document(playlist_id)

        doc = doc_ref.get()

        if not doc.exists:
            raise ValueError(f"Playlist id {playlist_id} does not exist")

        return UsersByPriorities(**doc.to_dict())
    

    def does_playlist_exist(self, playlist_id: str) -> bool:
        doc_ref = self.collection.document(playlist_id) 

        return doc_ref.get().exists

    def create_empty_document(self, playlist_id: str) -> None:
        doc_ref = self.collection.document(playlist_id)
        doc_ref.set({})

    def update_users_priorities(self, playlist_id: str, users_priorities: UsersByPriorities) -> None:
        doc_ref = self.collection.document(playlist_id)

        doc_ref.set(users_priorities.model_dump())
    
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
    delay: int = 30
    client: tasks_v2.CloudTasksClient = tasks_v2.CloudTasksClient()
    retry_url: str = ""
    retry_endpoint: str = ""

    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self, __context) -> None:
        self.retry_endpoint = f"{self.retry_url}/start"


    def push_classifier_reprocessing(self, playlist_id: str, message: str):
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
    import time
    playlist_id = "2elIaOB0fCHjcSABzQpfLD"
    
    publisher_client = PubsubPublisherClient()
    subscriber_client = PubsubSubscriberClient()
    firestore_client = FirestoreClient()

    print(firestore_client.get_users_priorities(playlist_id))

    users_priorities = UsersByPriorities(**{"high": ["11180277231"], "low": [], "medium": ["31qvemjqvhkkvdzfmkut24y4lsmy"]})
    firestore_client.update_users_priorities("test-test-test", users_priorities)

    print(firestore_client.get_users_priorities(playlist_id))



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
