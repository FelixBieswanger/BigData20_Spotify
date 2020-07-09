var isPlaying = false;
var songPaused = false;
var danceability;
var loudness;
var tempo;
var distance;
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
//const redirectUri = 'http://localhost:6969/'; //Whitelisted in Dashbaord
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

/** */
//window.onSpotifyPlayerAPIReady = () => {
window.onSpotifyWebPlaybackSDKReady = () => {
    console.log(_token)
    const player = new Spotify.Player({
    name: 'Live DJ Session',
    //getOAuthToken: cb => { cb(_token); },
    getOAuthToken: callback => { callback(_token);},
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
        
        //TO IMPLEMENT
        sendNewTrackToTopic(state.track_window.current_track.id)

        $('#current-track').attr('src', state.track_window.current_track.album.images[0].url); //Update Image
        $('#current-track-name').text(state.track_window.current_track.name); //Update Trackname

        var showArtists = '';
        for(let i = 0; i <= state.track_window.current_track.artists.length-1; i++){
            showArtists += state.track_window.current_track.artists[i].name;
            if(i != state.track_window.current_track.artists.length-1){
                showArtists += ", ";
            }
        }
        $('#artists').text(showArtists);
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


function get_dashboard_parameter(){
    loudness = Math.abs(parseInt(document.getElementById("Loudness").value));
    danceability = Math.abs(parseInt(document.getElementById("Danceability").value));
    tempo = Math.abs(parseInt(document.getElementById("Tempo").value));
    distance = Math.abs(parseInt(document.getElementById("Distance").value));


    alpha_loud = (loudness > 0) ? -1 : 1;
    alpha_dance = (danceability > 0) ? -1 : 1;
    alpha_tempo = (tempo > 0) ? -1 : 1;
    alpha_distance = (distance > 0) ? -1 : 1;

    var currentParametersJson = [
        { "parameter": "danceability", "alpha": alpha_loud, "weight": loudness },
        { "parameter": "loudness", "alpha": alpha_dance, "weight": danceability },
        { "parameter": "tempo", "alpha": alpha_tempo, "weight": tempo },
        { "parameter": "distance", "alpha": alpha_distance, "weight": distance }
    ];

    return currentParametersJson;
}


function save(){
    
    currentParametersJson = get_dashboard_parameter()
   
    $.ajax({
        url: "/api/parameters",
        type: "POST",
        data: JSON.stringify(currentParametersJson),
        success: function (msg) {
            //console.log(msg);
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
                //console.log(data)
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

function show_value4(x) {
    document.getElementById("slider_value4").innerHTML = x;
}


// Play a track using our new device ID
function play() {
    var uri = 'spotify:track:11dFghVXANMlKmJXsNCbNl';
    $.ajax({
        url: "https://api.spotify.com/v1/me/player/play?device_id=" + id,
        type: "PUT",
        data: '{"uris": ["' + uri + '"]}',
        beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + _token );},
        success: function(data) { 
            console.log("play");
        }
    });
}

function pause() {
    $.ajax({
        url: 'https://api.spotify.com/v1/me/player/pause?device_id=' + id,
        type: 'PUT',
        beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+ _token );},
        success: function(data) {
            console.log("pause")
        }
    });
}

function resume(){
    $.ajax({
        url: 'https://api.spotify.com/v1/me/player/play?device_id=' + id,
        type: 'PUT',
        beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + _token );},
        success: function(data) { 
            console.log("resume")
        }
    });
}

function previous(){
    $.ajax({
        url: 'https://api.spotify.com/v1/me/player/previous',
        type: 'POST',
        beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + _token );},
        success: function(data) {
            console.log("previous")
        }
    });
}

function skip(){
    $.ajax({
        url: 'https://api.spotify.com/v1/me/player/next',
        type: 'POST',
        beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + _token );},
            success: function(data) {
                console.log("skip")
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
            console.log("added song with id: " + songid + " to the queue")
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
    message = e.data;
    console.log(message);
    //addToQueue(message["id"]);
});


function sendNewTrackToTopic(songid){

    currentParametersJson = get_dashboard_parameter()

    $.ajax({
        //API
        url: "/parameters",
        type: "POST",
        data: JSON.stringify(currentParametersJson),
        success: function (msg) {
            console.log(msg);
        }
    });

    data = {
        "currentSong":songid
    }

    // Implement on fail
    $.ajax({
        url: "/currentSong",
        type: "POST",
        data: JSON.stringify(data),
        success: function(data) {
            console.log("sent track to topic")
        }
    });
}