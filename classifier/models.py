from pydantic import BaseModel, Field


class Priorities(BaseModel):
    low: list[str] = Field(default_factory=list)
    medium: list[str] = Field(default_factory=list)
    high: list[str] = Field(default_factory=list)


class PlaylistToPriorities(BaseModel):
    """
    Each playlist has 3 different priorities assigned, which stores 
    temporarily  
    """
    playlists: dict[str, Priorities] = Field(default_factory=dict)


class UsersByPriorities(BaseModel):
    low: set[str] = Field(default_factory=set)
    medium: set[str] = Field(default_factory=set)
    high: set[str] = Field(default_factory=set)


class PlaylistToUsersPriorities(BaseModel):
    """
    Each user in the playlist is assigned to a specific priority 
    """
    playlists: dict[str, UsersByPriorities] = Field(default_factory=dict)


if __name__ == "__main__":
    playlist_to_users_priorities = PlaylistToPriorities()
    # playlist_to_users_priorities.playlists["123-123-123"] = UsersByPriorities(low=["Alberto", "Julian"], medium=["Bartek"], high=["Mikołaj"])
    # playlist_to_users_priorities.playlists["123-123-123"].high.append("Witek")

    # users_by_priorities = UsersByPriorities(low=["Alberto", "Julian"], medium=["Bartek"], high=["Mikołaj"])
    
    data = {'high': [], 'low': ['11180277231'], 'medium': ['31qvemjqvhkkvdzfmkut24y4lsmy']}
    p = UsersByPriorities(**data)


    print(p["low"])
    # print(users_by_priorities)

    # for priority, users in users_by_priorities:
    #     print(priority, users)

    # playlist_to_users_priorities.playlists["123-123-124"] = UsersByPriorities()
    # playlist_to_users_priorities.playlists["123-123-124"].low.append("Jangas")

    # print(playlist_to_users_priorities)

    