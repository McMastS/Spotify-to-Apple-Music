import sys
from datetime import datetime
from flask import Flask, Response, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from port import PortPlaylist
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.static_folder = 'static'
app.template_folder = 'templates'
db = SQLAlchemy(app)

port = PortPlaylist(app.config['SPOTIFY_CLIENT_ID'],
                    app.config['SPOTIFY_CLIENT_SECRET'],
                    app.config['APPLE_TEAM_ID'],
                    app.config['APPLE_SECRET_KEY'],
                    app.config['APPLE_KEY_ID'])

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    spotify_link = db.Column(db.String(100), nullable=False)
    apple_link = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Playlist %r>' % self.name

@app.route('/')
def index():
    return redirect(url_for('playlist'))

@app.route('/login', methods=['POST'])
def login():
    # Reload port every time user logs in to ensure API tokens remain valid
    port.refresh_dev_tokens()
    port.set_a_user_token(request.json['Music-User-Token'])
    body = {}
    resp = Response(status=204)
    return resp

@app.route('/playlist/', methods=['GET', 'POST'])
@app.route('/playlist/<int:id>', methods=['DELETE'])
def playlist(id=None):
    if request.method == 'POST':
        # TODO: Show tracks not found after creating playlist
        resp, _not_found = port.port_playlist(request.form['spotifyLink'],
                                              request.form['applePlaylistName'],
                                              description=request.form['applePlaylistDesc'])

        spotify_link = request.form['spotifyLink']
        apple_link = resp['data'][0]['href']
        name = request.form['applePlaylistName']
        desc = request.form['applePlaylistDesc']
        new_playlist = Playlist(name=name, description=desc,
                                spotify_link=spotify_link, apple_link=apple_link)
        try:
            db.session.add(new_playlist)
            db.session.commit()
        except:
            return 'Something went wrong inserting into database.'
        return redirect(url_for('history'))

    if request.method == 'DELETE':
        playlist_to_delete = Playlist.query.get_or_404(id)
        print(playlist_to_delete, file=sys.stderr)
        try:
            db.session.delete(playlist_to_delete)
            db.session.commit()
        except:
            return 'Something went wrong deleting.'

        body = {}
        resp = Response(body, status=204)
        return resp

    
    return render_template('playlist.html', a_dev_token=port.a_dev_token)

@app.route('/history', methods=['GET'])
def history():
    history = Playlist.query.order_by(Playlist.date_added).all()
    return render_template('history.html', history=history)

if __name__ == "__main__":
    app.run(debug=True)
