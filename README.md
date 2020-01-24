# Spotify-to-Apple-Music

I find myself enjoying Spotify playlists much more than I enjoy the Apple Music playlists, so I decided to create this web app to port any
Spotify playlist to an Apple Music account. This project is still ongoing, and I will update this doc whenever I make progress.

To run on your machine:
Obtain the necessary IDs and Secrets from Apple Music and Spotify, then create and add them to a 'config.py' file. An example can be found in the 'example_config.py'. Then:
    
    pip install -r requirements.txt
    flask run



Todo:
1. ~~The app became much bigger than expected, so reorganize the code using Flask best practices for structure (done)~~
2. ~~Display all created playlists somewhere (done)~~
3. ~~Add a login/user account functionality (won't complete). Instead of a user functionality, I realized it would be a much better user experience to just authorize on Apple Music on every 'create playlist' click~~
4. ~~Improve the searching when creating a playlist~~ (done)
5. ~~Allow playlists of over 25 songs to be ported~~ (done)
6. Improve duplicate recognition (duplicates come in with artists who have songs in multiple languages, like Andrea Bocelli, and with artists whose songs have been covered frequently) 
7. Deploy somewhere
