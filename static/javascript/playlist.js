document.addEventListener('musickitloaded', () => {
    // MusicKit global is now defined
    // Dev token is defined in the template
    // TODO: Don't define dev token in the template...
    const music = MusicKit.configure({
      developerToken: aDevToken,
      app: {
        name: 'spotify2apple',
        build: '0.1'
      }
    });

    document.getElementById('migrate-btn').addEventListener('click', () => {
        music.authorize().then(async musicUserToken => {
            // "Login" by setting the musicUserToken
            await fetch('http://localhost:5000/login', {
                method: 'POST',
                body: JSON.stringify({'Music-User-Token': musicUserToken}),
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(response => {
                if (!response.ok) {
                    alert('Something went wrong with your Apple ID Authentication. Please try again.'); 
                } else {
                    document.getElementById('playlist-form').submit();
                }
            })
        });
    });
  });
