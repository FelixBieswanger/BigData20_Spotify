var isPlaying = false;
var songPaused = false;

var danceability;
var loudness;
var tempo;
var distance;
var currentTrackName;
var currentTrackArtist;
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
//const redirectUri = 'http://40.74.218.18:6969/'; //Whitelisted in Dashbaord
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
var currentSongId = {"id":"11dFghVXANMlKmJXsNCbNl"};
var searchResult;

// Set up the Web Playback SDK

/** */
window.onSpotifyPlayerAPIReady = () => {
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

        //Display album cover in background.
        $('#songcover').css('background-image', 'url("' + state.track_window.current_track.album.images[0].url + '")')

        //Display songname and artist in the webplayer.
        $('#songname').text(state.track_window.current_track.name);
        $('#artist').text(state.track_window.current_track.artists[0].name);

        //Display artist cover. 
        displayArtistCover(state.track_window.current_track.artists[0].uri);
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

//Get the selected values from the slider in the UI.
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

//Display the artist portrait withing the webplayer.
function displayArtistCover(artistid){
    slicedArtistId = artistid.slice(15,37);
    console.log(slicedArtistId);
    $.ajax({
        url:"https://api.spotify.com/v1/artists/" + slicedArtistId,
        type:"GET",
        beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + _token );},
            success: function(data){
                $('#artistcircle').css('background-image', 'url(' + data.images[0].url + ')');
            }
    })
}

//Save the Users preferences for his next recommended song.
//Make a POST request to the recommendation engine with the value of the UI Slider Elements.
function save(){

    currentParametersJson = get_dashboard_parameter()
    /**
    $.ajax({
        crossOrigin: true,
        url: "http://40.119.27.3:6969/parameters/",
        type: "POST",
        data: JSON.stringify(currentParametersJson),
        success: function (msg) {
            //console.log(msg);
        }
    });
    */

    getCurrentTrack();

    var xhr1 = new XMLHttpRequest();
    xhr1.open("POST", 'http://40.119.27.3:6969/currentSong', true);

    //Send the proper header information along with the request
    xhr1.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr1.onreadystatechange = function () { // Call a function when the state changes.
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            // Request finished. Do processing here.
            console.log(xhr1.responseText);
            console.log("sent current song");
        }
    }

    data = {
        "current_song": currentSongId["id"]
    }
    console.log(data)
    xhr1.send(JSON.stringify(data));


    var xhr = new XMLHttpRequest();
    xhr.open("POST", 'http://40.119.27.3:6969/parameters', true);

    //Send the proper header information along with the request
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onreadystatechange = function () { // Call a function when the state changes.
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            // Request finished. Do processing here.
            console.log(xhr.responseText);
        }
    }
    xhr.send(JSON.stringify(currentParametersJson));
}

//Call this function when the play/pause button is pressed by the User.
//Determine if the Webplayer should Play, Pause or resume based on isPlaying and songPaused.
function songHandler(){
    if(isPlaying){
        pausePlayer();
        isPlaying = false;
        songPaused = true;
    } else if(!isPlaying && !songPaused){
        play();
        isPlaying = true;
    } else {
        resumePlayer();
        isPlaying = true;
        songPaused = false;
    }
}

//Get Song features for the currently playing track in the Users Playback.
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

//Get the currently playing track in the Users Playback.
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

//Show slider Values.
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


//Start the Users Playback.
//This will always play the same song by default and get recommendations based on this same song.
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


//Pause the currently playing Song in the Users Playback.
function pausePlayer() {
    $.ajax({
        url: 'https://api.spotify.com/v1/me/player/pause?device_id=' + id,
        type: 'PUT',
        beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer '+ _token );},
        success: function(data) {
            console.log("pause");
        }
    });
}

//Resume the currently playing Song in the Users Playback. 
//Note that this function can only be called if a Song in this session was previously paused.
function resumePlayer(){
    $.ajax({
        url: 'https://api.spotify.com/v1/me/player/play?device_id=' + id,
        type: 'PUT',
        beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + _token );},
        success: function(data) {
            console.log("resume");
        }
    });
}

//go to the previously played Song
function previous(){
    $.ajax({
        url: 'https://api.spotify.com/v1/me/player/previous',
        type: 'POST',
        beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + _token );},
        success: function(data) {
            console.log("previous");
            if(isPlaying == false);
        }
    });
}

//skip the currently playing Song
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


//Adding a new Song to the Users Playback Queue
function addToQueue(songid){
    var uri = 'spotify:track:' + songid
    $.ajax({
        url: 'https://api.spotify.com/v1/me/player/queue?&uri=' + uri,
        type: 'POST',
        beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + _token );},
        success: function(data) {
            console.log("added song with id: " + songid + " to the queue")

            $.ajax({
                url: 'https://api.spotify.com/v1/tracks/' + songid,
                type: 'GET',
                beforeSend: function(xhr){xhr.setRequestHeader('Authorization', 'Bearer ' + _token );},
                success: function(data){
                    console.log('hab info über gequeten song!');
                    console.log(data);
                    currentTrackName = data.name;
                    currentTrackArtist = data.artists[0].name;
                    displayNewRecommendation();
                }
            });
        }
    });
}

//Post a notification to display the new recommendation the user just received.
function displayNewRecommendation(){
    let message = document.createTextNode('Neue Recommendation erhalten!');
    let info = document.createTextNode(currentTrackArtist + ' - ' + currentTrackName);
    var d = document.createElement('div');
    var innerDiv1 = document.createElement('div');
    var innerDiv2 = document.createElement('div');
    d.setAttribute("class", "notification");
    innerDiv1.appendChild(message);
    innerDiv2.appendChild(info);
    d.appendChild(innerDiv1);
    d.appendChild(innerDiv2);
    let feed = document.getElementById('notificationcontainer');
    feed.appendChild(d);

}

function changeIcon(){
    $(".playpause").toggleClass("fa-pause-circle")
    $(".playpause").toggleClass("fa-play-circle")
}

//New recommendations from recommendation engine.

var source = new EventSource("http://40.119.27.3:6969/recomendations");

source.addEventListener("message", function (e) {
    message = JSON.parse(e.data.substring(2,e.data.length-1));
    addToQueue(message["id"]);
});

//Sending the currently playing track to the recommendation engine.
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
