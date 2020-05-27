import requests
import json
import time
import matplotlib.pyplot as plt

with open("secrets.json","r") as file:
    secrets = json.load(file)

CLIENT_ID = secrets["CLIENT_ID"]
CLIENT_SECRET = secrets["CLIENT_SECRET"]

grant_type = 'client_credentials'
body_params = {'grant_type': grant_type}

url = 'https://accounts.spotify.com/api/token'
response = requests.post(url, data=body_params,
                         auth=(CLIENT_ID, CLIENT_SECRET))

token_raw = json.loads(response.text)
token = token_raw["access_token"]

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    "Authorization": "Bearer {}".format(token),
}

params = (
    ('limit', '1'),
    ('seed_genres', 'charts,pop,hits,new'),
    ('min_acousticness', '0.5'),
)

response = requests.get(
    'https://api.spotify.com/v1/recommendations', headers=headers, params=params)

result = json.loads(response.content)
track = result["tracks"][0]
id = track["id"]
name = track["name"]+" from "+track["artists"][0]["name"]
print(name)

response = requests.get("https://api.spotify.com/v1/audio-analysis/"+id,headers=headers)
result = json.loads(response.content)

sections = result["sections"]
segments = result["segments"]

time = 0
for sec in sections:
    time += sec["duration"]
print(len(sections), "sections; total duration", time)
print(sections[0])
print()
time=0
for seg in segments:
    time += seg["duration"]
print(len(segments), "segments; total duration", time)
print(segments[1])


x = list()
loud = list()
pitch = list()

for seg in segments:
    if segments.index(seg) == 0:
        x.append(0)
    else:
        x.append(seg["start"])

    loud.append(seg["loudness_max"])
    pitch.append(seg["pitches"].index(max(seg["pitches"])))


plt.plot(x,pitch,label="pitch")
plt.legend()
plt.title(name)
plt.yticks([i for i in range(12)],["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"])
plt.show()




"""
start = list()
loudness = list()
tempo = list()

for sec in sections:
    if sections.index(sec) == 0:
        start.append(0)
    else:
        start.append(sec["start"])

    loudness.append(sec["loudness"])
    tempo.append(sec["tempo"])

print(start)
print(tempo)
print(loudness)


plt.plot(start,tempo,label="tempo")
plt.plot(start,loudness, label="loudness")
plt.xticks(start)
plt.title(name)
plt.legend()
plt.show()

"""





