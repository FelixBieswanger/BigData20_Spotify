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
	  'user-read-private'
	];

	// If there is no token, redirect to Spotify authorization
	if (!_token) {
	  window.location = `${authEndpoint}?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scopes.join('%20')}&response_type=token&show_dialog=true`;
	}

    var id = '';
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
	   });

	  // Ready
    player.on('ready', data => {
        console.log('Ready with Device ID', data.device_id);
		id = data.device_id;
		// Play a track using our new device ID
        
	   });
    
	  // Connect to the player!
    player.connect();
	   }
    // HTTP Request to start whichever song uri is currently pasted into the textbox!
	function play() {
        var uri = $('#songname').val();
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
