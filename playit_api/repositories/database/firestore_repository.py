from google.cloud import firestore

class FirestoreRepository:
    firestore_client: firestore.Client = firestore.Client()
    document_name: str = "playlist_user_id"

    def playlist_exists(self, playlist_id: str) -> bool:
        doc_ref = self.firestore_client.collection(self.document_name).document(playlist_id)
        doc = doc_ref.get()

        # if not doc.exists:

        return doc.exists

    def save_playlist_id(self, playlist_id: str) -> None:
        doc_ref = self.firestore_client.collection(self.document_name).document(playlist_id)
        doc_ref.set({})


    def save_user_id(self, playlist_id: str, user_id: str, username: str) -> None:
        doc_ref = self.firestore_client.collection(self.document_name).document(playlist_id)
        doc_ref.update(
            {user_id: username}
        )
        # doc_ref.update(
        #     {"users_ids": firestore.ArrayUnion([user_id])}
        # )


    def get_users_ids(self, playlist_id: str) -> dict:
        doc_ref = self.firestore_client.collection(self.document_name).document(playlist_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise ValueError(f"Playlist id {playlist_id} does not exist")
        
        data = doc.to_dict()

        return data
    
    def delete_playlist_id(self, playlist_id: str) -> None:
        self.firestore_client.collection(self.document_name) \
            .document(playlist_id) \
            .delete()
    
    

        



if __name__ == "__main__":
    firestore_repository = FirestoreRepository()

    # firestore_repository.save_playlist("123-123-123-124")
    # firestore_repository.save_user_id("123-123-123-124", "gruba kinga")
    data = firestore_repository.get_users_ids("123-123-123-124")
    print(data)