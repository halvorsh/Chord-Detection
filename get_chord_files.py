import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re

base = "https://www.scales-chords.com/"

index_to_note = ["C","C%23","D","Eb","E","F","F%23","G","Ab","A","Bb","B"]
type_of_chord = ["Major", "Minor", "Dim", "Aug", "Sus2", "Sus4", "Maj7", "min7", "7"]

all_chords = []
for note in index_to_note:
    for type in type_of_chord:
        all_chords.append(note + type)

for chord in tqdm(all_chords):
    html = requests.get("https://www.scales-chords.com/chord/guitar/" + chord)
    result = html.content
    doc = BeautifulSoup(result, 'lxml')
    goal = doc.find_all("source", type="audio/mpeg")

    for source in goal:
        filename = source['src'][20:]
        r = requests.get(base + source['src'])
        output = "../Chord Sounds/" + filename
        with open(output, 'wb') as f:
            f.write(r.content)

        filename = re.sub('fast', 'slow', filename)
        output = "../Chord Sounds/" + filename
        r = requests.get(base + source['src'])
        with open(output, 'wb') as f:
            f.write(r.content)
