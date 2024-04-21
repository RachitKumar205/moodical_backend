client_ID='e2d12b171e824b4ba99f26afada7b99a'       # Fill in with the value from the Spotify Developer Dashboard
client_SECRET='6a937faa890d4108b4e3aed3ee12a681'   # Fill in with the value from the Spotify Developer Dashboard
redirect_URI="http://localhost:[PORT]]/music/callback"  # Fill in with the port you want to use -- MUST be one of the
                                                                   # redirect urls as in Spotify Developer Dashboard
scope = "user-read-private playlist-read-private playlist-modify-public user-top-read"  # Set the scope(s)