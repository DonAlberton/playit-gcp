# TODO
0. Change naming to grant better readability
    * Spotify Client - playlist_users -> playlist_to_user_ids
    * Classifier - priorities_assiged -> users_priorities
    * Scheduler - priorities -> queues_wages

1. Remove all the values from the priority queues when the user stops the 
session. If not removed, there will still be some tracks from other sessions
2. Scale the application, so it can be used by multiple users (every new user is a new task in the event loop). It would also need changes in how Redis stores the priorities queues, eg. low:<playlist-id-1>, medium:<playlist-id-1>,
high:<playlist-id-1>, low:<playlist-id-2>, ... 
3. Make it Cloud Native
    * Make containers stateless (temporary data is stored on Azure tables, so in case of failure a new container can read it)
        * Spotify Client - playlist_users
        * Classifier - priorities_assiged, input_playlist_id, queues 
        * Scheduler - output_playlist_id
4. Make the output playlist private, so no unwanted user can access it.
5. Change classifier class from Priorities to QueuePriorities
5. Add traces to the application
6. Do not let starting multiple tasks on /start endpoint both on classifier and scheduler
7. Change apps port to 8000


Copyright (c) 2025 Alberto Szpejewski. All Rights Reserved.
Ten projekt jest udostępniany wyłącznie w celu recenzji. Jakiekolwiek użycie, modyfikacja lub rozpowszechnianie wymaga pisemnej zgody autora.
