# Pythonify
A super simple python api for spotify. Has support for searching songs, artists, and albums, as well as creating personal playlists.
# Features
* Search tracks, artists, and albums
* Create playlists
* All authentication handled by backend
# Instructions
* To retrieve information about an artist, call the get_artist() function and pass in the id of the artist which can be retrieved from teh spotify app.
* To retrieve information about an album, call the get_album() function and pass in the id of the album which can be retrieved from the spotify app.
* To retrieve information about a track, call the get_track() function and pass in the name of the track.
* To create a playlist, call the create_playlist method and pass in values for the name and description for the playlist
# Possible Issues
* Track results may return the wrong track due to the simplicity of the parseing of the get_track() results.
