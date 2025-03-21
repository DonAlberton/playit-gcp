from dataclasses import dataclass

@dataclass
class Track:
    track_id: str
    added_by_id: str

    def __init__(self, track_id, added_by_id):
        self.track_id = track_id
        self.added_by_id = added_by_id