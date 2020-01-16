# Spotify-to-Apple-Music

I find myself enjoying Spotify playlists much more than I enjoy the Apple Music playlists, so I decided to create this web app to port any
Spotify playlist to an Apple Music account. This project is still ongoing, and I will update this doc whenever I make progress.

To run on your machine:
Obtain the necessary IDs and Secrets from Apple Music and Spotify, then create and add them to a 'config.py' file. An example can be found in the 'example_config.py'. Then:
    
    pip install -r requirements.txt
    flask run



Todo:
1. The app became much bigger than expected, so reorganize the code using Flask best practices for structure (done)
2. Display all created playlists somewhere (done)
3. Add a login/user account functionality (won't complete). Instead of a user functionality, I realized it would be way easier
    to just authorize on Apple Music on every 'create playlist' click
4. Improve the searching when creating a playlist
5. Deploy (probably using Heroku)
