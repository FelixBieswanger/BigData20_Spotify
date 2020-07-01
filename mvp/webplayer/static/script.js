var isPlaying = false;
var songPaused = false;
var danceability;
var loudness;
var tempo;
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
const redirectUri = 'http://localhost:6969/'; //Whitelisted in Dashbaord
const scopes = [
    'streaming',
    'user-read-email',
    'user-read-private',
    'user-modify-playback-state',
    'user-read-currently-playing'
];

// If there is no token, redirect to Spotify authorization
if (!_token) {
    window.location = `${authEndpoint}?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scopes.join('%20')}&response_type=token&show_dialog=true`;
}

var id = '';
var currentSongId;
var searchResult;

/**var nextSong = new EventSource("/songs");

nextSong.addEventListener("message", function(songid){
    songid = JSON.parse(songid.data);
    addToQueue(songid);
});**/
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

function save(){
    loudness = document.getElementById("Loudness").value;
    danceability = document.getElementById("Danceability").value
    tempo = document.getElementById("Tempo").value

    var currentParametersJson = {"parameters":
        {
            "danceability":{
                "alpha": danceability,
                "weight": 2
            },
            "loudness":{
                "alpha": loudness,
                "weight": 2
            },
            "tempo":{
                "alpha": tempo,
                "weight": 2
            }
        }
    }
    //getCurrentTrack();

    $.ajax({
        url: "http://localhost:6969/formdata",
        type: "POST",
        data: JSON.stringify(currentParametersJson),
        success: function (msg) {
            console.log(msg);
            console.log("heY");
        }
    });

    //console.log(currentParametersJson);
    
}

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

//get Song features for the current track
function getFeatures(){
    $.ajax({
    url:"https://api.spotify.com/v1/audio-features/" + getCurrentTrack().data,
    type:"GET",
    data:"danceability" + "loudness" + "tempo",
    beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + _token );},
            success: function(data) {
                console.log(data)
            }
    })

}

//get the currently playing track
function getCurrentTrack (){
    $.ajax({
    url: "https://api.spotify.com/v1/me/player/currently-playing",
    type: "GET",
    beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + _token );},
            success: function(data) {
                console.log(data);
                currentSongId = {"id": data.item.id};
                console.log(currentSongId);
            }
    })
}
//Wert der Slider anzeigen
function show_value1(x){
    document.getElementById("slider_value1").innerHTML=x;
}

function show_value2(x){
    document.getElementById("slider_value2").innerHTML=x;
}

function show_value3(x){
    document.getElementById("slider_value3").innerHTML=x;
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

function addToQueue(songid){
    var uri = 'spotify:track:' + songid
    $.ajax({
        url: 'https://api.spotify.com/v1/me/player/queue?&uri=' + uri,
        type: 'POST',
        beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + _token );},
        success: function(data) {
            console.log(data)
        }
    });
}

function readJson(){
    $.getJSON("/static/message.json", function(json){
        console.log(json);
        addToQueue(json.id);
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




//TO DO IMPLEMENT NEW RECOMENDATION

var source = new EventSource("/recomendations");

source.addEventListener("message", function (e) {
    message = JSON.parse(e.data);
    addToQueue(message["id"]);
});