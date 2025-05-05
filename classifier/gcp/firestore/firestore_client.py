from models.users_by_priorities import UsersByPriorities
from google.cloud import firestore


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