from google.cloud import firestore

class FirestoreClient:
    firestore_client: firestore.Client = firestore.Client()
    document_name: str = "input_to_output_playlists"
    collection: firestore.Client.collection = firestore_client.collection(document_name)

    def set_input_output_playlist(
        self, 
        input_playlist_id: str,
        output_playlist_id: str
    ) -> None:
        doc_ref = self.collection.document(input_playlist_id)

        doc_ref.set({input_playlist_id: output_playlist_id})


    def get_output_playlist_id(self, input_playlist_id: str) -> str:
        doc_ref = self.collection.document(input_playlist_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise ValueError(f"Playlist id {input_playlist_id} does not exist")
        
        return doc.to_dict().get(input_playlist_id)


if __name__ == "__main__":
    fc = FirestoreClient()

    # fc.set_input_output_playlist("123-123-123", "123-123-124")
    print(fc.get_output_playlist_id("123-123-123"))