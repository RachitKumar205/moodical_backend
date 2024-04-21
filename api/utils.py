import pathlib
import textwrap
#from google.colab import userdata
import google.generativeai as genai
import requests

#from IPython.display import display
#from IPython.display import Markdown


#def to_markdown(text):
#  text = text.replace('•', '  *')
#  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

GOOGLE_API_KEY='AIzaSyDBrzGLFztYZZA2xQ6MSbYztjcVZvwhQDE'

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-1.5-pro-latest')

def music():
  response = model.generate_content("Recommend music to improve mood, with one from each genre")
  print(response.text)
def pre_exist(comorb):
  response = model.generate_content(f"Psychiatric medicines that cannot be taken if a person suffers from {comorb}")
  print(response.text)

def meds(medication):
  response = model.generate_content(f"Psychiatric medicines that cannot be taken with {medication}")
  print(response.text)

def psych_meds(risk):
  response = model.generate_content(f"Psychiatric medicines that increase {risk} risk")
  print(response.text)

def psy_meds(diagnosis):
  response = model.generate_content(f"Psychiatric medicines for {diagnosis} and common side-effects")
  print(response.text)


def recommend_songs(songs, mood):
  print(songs)
  prompt = f"select songs from this list and give a space seperated list of all the song uris from the list I am providing you here. Select atleast 20 songs. The songs should help the user feel better and uplift their mood. The current mood of the user is {mood}. Order the songs randomly. For example, a sample output would be uri1 uri1 uri3 seperated by a space. Do NOT give any more text.: {songs}"
  response = model.generate_content(prompt)
  print(response.text.split())
  print(response.prompt_feedback)
  return response.text.split()

def recommend_movies(mood):
  prompt = f"Recommend 3 to 5 movies to the user and give a space seperated list of the movie names just from memory. Make sure to only recommend movies that have one word titles. The movies should help the user feel better and uplift their mood. The current mood of the user is {mood}. For example, a sample output would be cars inception barbie seperated by a space. Do NOT give any more text."
  response = model.generate_content(prompt)
  print(response.text.split())
  print(response.prompt_feedback)
  return [movie(m) for m in response.text.split()]

def movie(movie_name):
  url = "https://www.imdb.com/find/?q="
  movie_name = movie_name.split()
  url = url + movie_name[0]
  for i in range(1, len(movie_name)):
    url = url + "%20" + movie_name[i]

  from bs4 import BeautifulSoup
  import requests

  headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}

  response = requests.get(url, headers=headers)
  content = BeautifulSoup(response.content, "html.parser")

  content = content.find("div", "ipc-metadata-list-summary-item__tc")
  content = content.find("a")
  content = str(content)
  content = content.split('"')
  content = content[5]
  print(content)

  url_title = "https://www.imdb.com/" + content

  response_1 = requests.get(url_title, headers=headers)
  content_1 = BeautifulSoup(response_1.content, "html.parser")
  content_image = content_1.find("div",
                                 "ipc-media ipc-media--poster-27x40 ipc-image-media-ratio--poster-27x40 ipc-media--baseAlt ipc-media--poster-l ipc-poster__poster-image ipc-media__img")
  content_image = str(content_image.find("img"))
  content_image = content_image.split('"')

  print("Image:", content_image[9])
  image = content_image[9]

  content_description = content_1.find("p", "sc-466bb6c-3 fOUpWp")
  content_description = str(content_description.find("span"))
  content_description = content_description.split(">")
  content_description = content_description[-2].replace('"', '').replace("</span", "")
  print("Description:", content_description)
  desc = content_description

  return {"link": url_title, "image": image, "description": desc}


movie("Mission Impossible")

def create_spotify_playlist(access_token, user_id, name):
  url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
  headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
  }
  data = {
    "name": name,
    "public": False
  }

  try:
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
      playlist_data = response.json()
      print(playlist_data["id"])
      return [playlist_data["external_urls"]['spotify'], playlist_data["id"]]
    else:
      print(f"Failed to create playlist. Status code: {response.status_code}")
      return None
  except Exception as e:
    print(f"Error occurred: {e}")
    return None

def add_tracks_to_playlist(access_token, playlist_id, track_uris):
  url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
  headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
  }
  print(type(track_uris))
  data = {
    "uris": track_uris,
    "position": 0
  }

  try:
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
      print("Tracks added to playlist successfully!")
    else:
      print(f"Failed to add tracks to playlist. Status code: {response}")
  except Exception as e:
    print(f"Error occurred: {e}")