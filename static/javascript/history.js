function delete_playlist(id) {
    console.log(id);  
    fetch('http://localhost:5000/playlist/' + id, {  
        method: 'DELETE'
    }).then(response => {
        if (!response.ok) {
            alert('Something went wrong deleting the playlist. Please reload and try again.')
        }
    });
}