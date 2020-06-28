	var isPlaying = false;
    var songPaused = false;
    // Get the hash of the url
	const hash = window.location.hash
	.substring(1)
	.split('&')
	.reduce(function (initial, item) {
		if (item) {
			var parts = item.split('=');
			initial[parts[0]] = decodeURIComponent(parts[1]);
		}
		return initial;
	}, {});
	
	window.location.hash = '';

	// Set token
	let _token = hash.access_token;
	const authEndpoint = 'https://accounts.spotify.com/authorize';

	// Replace with your app's client ID, redirect URI and desired scopes
	const clientId = '37e56ecffd2e4712a07bfcf7ac4ec508'; //DashboardID
	const redirectUri = 'http://localhost/spotifybigdata/index.html'; //Whitelisted in Dashbaord
	const scopes = [
        'streaming',
        'user-read-email',
        'user-read-private',
        'user-modify-playback-state'
	];

	// If there is no token, redirect to Spotify authorization
	if (!_token) {
	  window.location = `${authEndpoint}?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scopes.join('%20')}&response_type=token&show_dialog=true`;
	}

    var id = '';
    var currentSong;
    var searchResult; 
	// Set up the Web Playback SDK

	window.onSpotifyPlayerAPIReady = () => {
	  const player = new Spotify.Player({
		name: 'Live DJ Session oder so',
		getOAuthToken: cb => { cb(_token); },
        volume: 0.5
	  });

	// Error handling
	player.addListener('initialization_error', ({ message }) => { console.error(message); });
	player.addListener('authentication_error', ({ message }) => { console.error(message); });
	player.addListener('account_error', ({ message }) => { console.error(message); });
	player.addListener('playback_error', ({ message }) => { console.error(message); });


	  // Playback status updates
    player.on('player_state_changed', state => {
		console.log(state) //Standard SDK
		$('#current-track').attr('src', state.track_window.current_track.album.images[0].url); //Update Image
		$('#current-track-name').text(state.track_window.current_track.name); //Update Trackname
        $('#current-track-artist').text(state.track_window.current_track.artists[0].name);
        $('#current-track-artist2').text(state.track_window.current_track.artists[1].name);
	   });

	  // Ready
    player.on('ready', data => {
        console.log('Ready with Device ID', data.device_id);
		id = data.device_id;	
	   });
    
	  // Connect to the player!
    player.connect();
    }
    
    var slider = document.getElementById("myRange");
    var output = document.getElementById("demo");
    output.innerHTML = slider.value; // Display the default slider value

    // Update the current slider value (each time you drag the slider handle)
    slider.oninput = function() {
    output.innerHTML = this.value;
    }

    function save(save){

    }

    function reset(){
       index.getElementById('Loudness').value = 3;
       index.getElementById('Danceability').value = 3;
       index.getElementById('...').value = 3;


    };
    
    function songHandler(){
        if(isPlaying){
            pause();
            isPlaying = false;
            songPaused = true;
        } else if(!isPlaying && !songPaused){
            play();
            isPlaying = true;
        } else {
            resume();
            isPlaying = true;
            songPaused = false;
        }
    }
    
    // Play a track using our new device ID
	function play() {
        var uri = 'spotify:track:0ed6evAMZvewGh4UI9KkVU", "spotify:track:0I67c6jPoBxVkUwo02bZnD';
		$.ajax({
			url: "https://api.spotify.com/v1/me/player/play?device_id=" + id,
			type: "PUT",
			data: '{"uris": ["' + uri + '"]}',
			beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + _token );},
			success: function(data) { 
				console.log(data)
			}
		});
	}

    function pause() {
        $.ajax({
            url: 'https://api.spotify.com/v1/me/player/pause?device_id=' + id,
            type: 'PUT',
            beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+ _token );},
            success: function(data) {
                console.log(data)
            }
        });
    }

    function resume(){
        $.ajax({
            url: 'https://api.spotify.com/v1/me/player/play?device_id=' + id,
            type: 'PUT',
            beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + _token );},
			success: function(data) { 
				console.log(data)
			}
        });
    }

    function previous(){
        $.ajax({
            url: 'https://api.spotify.com/v1/me/player/previous',
            type: 'POST',
            beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + _token );},
			success: function(data) {
				console.log(data)
			}
        });
    }

    function skip(){
        $.ajax({
            url: 'https://api.spotify.com/v1/me/player/next',
            type: 'POST',
            beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + _token );},
                success: function(data) {
                    console.log(data)
                }
            });
    }
    
    function search(){
        var searchcontext = $('#searchbox').val();
        console.log(searchcontext)
        
        //const myData = {
        //    q: searchcontext,
        //    type: "track"
        //}
        
        /**$.ajax({
            url: 'https://api.spotify.com/v1/search?q=' + searchcontext + '&type=track',
            type: 'GET',
            //data: JSON.stringify(myData),
            beforeSend: function(xhr){
                xhr.setRequestHeader('Accept', 'application/json')
                xhr.setRequestHeader('Content-Type', 'application/json')
                xhr.setRequestHeader('Authorization', 'Bearer ' + _token)
            },
            success: function(data) {
                console.log(data)
            }
        })
        
        /**$.get('https://api.spotify.com/v1/search?q=' + searchcontext + '&type=track', { beforeSend: function(xhr){
            xhr.setRequestHeader('Authorization', 'Bearer ' + _token ); }
        })**/
        
        fetch(
            'https://cors-anywhere.herokuapp.com/api.spotify.com/v1/search?q=' + searchcontext + '&type=track&market=de',
            {
                headers: {
                    Authorization: 'Bearer ' + _token,
                }
            }
        )
        .then(result => result.json()).then(result => 
            displayResults(result)
        )
        
    }
    
    //hier schleifendurchläufe an ergebnisse anpassen. beim api call evtl ergebnisse limitieren.
    function displayResults(result){
        var span = '#search-res-'
        console.log(result)
        for(j = 0; j <= result.tracks.items.length-1; j++) {
            $(span.concat(j)).text(result.tracks.items[j].name + ' - ' + result.tracks.items[j].artists[0].name);
        }
    }

    function changeIcon(){
        $(".playpause").toggleClass("fa-pause-circle")
        $(".playpause").toggleClass("fa-play-circle")
    }
