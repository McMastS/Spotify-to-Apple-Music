from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from port import PortPlaylist
import sys
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.static_folder = 'static'
app.template_folder ='templates'
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
    return render_template('index.html', a_dev_token=port.a_dev_token)

@app.route('/login', methods=['POST'])
def login():
    # Reload port every time user logs in to ensure API tokens remain valid
    port.refresh_dev_tokens()
    port.set_a_user_token(request.json['Music-User-Token'])
    return redirect(url_for('playlist'))

@app.route('/playlist', methods=['GET', 'POST'])
def playlist():
    if request.method == 'POST':
        resp, not_found = port.port_playlist(request.form['spotifyLink'], request.form['applePlaylistName'], description=request.form['applePlaylistDesc'])

        spotify_link = request.form['spotifyLink']
        apple_link = resp['data'][0]['href']
        name = request.form['applePlaylistName']
        desc = request.form['applePlaylistDesc']
        new_playlist = Playlist(name=name, description=desc, spotify_link=spotify_link, apple_link=apple_link)
        try:
            db.session.add(new_playlist)
            db.session.commit()
        except Exception as e:
            print(e, file=sys.stderr)
            return 'Something went wrong'
        return redirect(url_for('history'))
    
    if port.am.user_access_token:
        return render_template('playlist.html')
    else:
        return redirect(url_for('index'))

@app.route('/history', methods=['GET'])
def history():
    history = Playlist.query.order_by(Playlist.date_added).all()
    return render_template('history.html',history=history)

if __name__ == "__main__":
    app.run(debug=True)
