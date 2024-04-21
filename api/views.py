import string
from random import choices

import cv2
import numpy as np
import requests
import spotipy
from allauth.socialaccount.models import SocialToken
from django.http import HttpResponseRedirect, JsonResponse
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.urls import reverse

from django.core.files import File
from django.contrib.auth import authenticate

import base64
from argparse import Namespace

from spotipy import SpotifyOAuth

from api.models import *
from api.utils import recommend_songs, create_spotify_playlist, add_tracks_to_playlist, recommend_movies
from moodifymodel.recog3 import class_labels, return_mood

# def get_ip(request):

#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

#     if x_forwarded_for:

#         ip = x_forwarded_for.split(',')[0]

#     else:

#         ip = request.META.get('REMOTE_ADDR')

#     return ip


class MoodDetectViewSet(ViewSet):

    BASE_URL = "https://localhost:8000"

    def image_analysis(self, request):
        data = request.data
        data = Namespace(**data)
        token = data.token
        token = Token.objects.filter(key=token).first()
        songs = []
        bypass = True
        mood = "Error try again"

        if bypass:
            try:
                image_data = data.image
                if image_data:
                    image_data = image_data.split(',')[1]
                    image_data = base64.b64decode(image_data)

                    # Convert base64 data to numpy array
                    nparr = np.fromstring(image_data, np.uint8)
                    # Decode numpy array as image
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    if image is not None:
                        # Proceed with OpenCV processing
                        file_name = "mood_image.jpg"
                        cv2.imwrite(file_name, image)

                        # Integrate the ML model
                        model_op = return_mood(file_name)
                        if isinstance(model_op, int):
                            mood = class_labels[int(model_op)]
                            # Rest of your code for processing mood and songs...
                            # ...
                            return Response({"mood": mood, "songs": songs})

                        else:
                            return Response({"error": "Failed to process image"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"error": "Failed to decode image data"}, status=status.HTTP_400_BAD_REQUEST)

                else:
                    return Response({"error": "No image data provided"}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

def generate_random_string(length):
    return ''.join(choices(string.ascii_letters + string.digits, k=length))

class SpotifyLoginView(APIView):

    def get(self, request):
        client_id = 'e2d12b171e824b4ba99f26afada7b99a'  # Replace with your Spotify client ID
        redirect_uri = 'http://localhost:3000/signup'  # Replace with your redirect URI
        scope = 'user-read-private user-read-recently-played user-read-email user-library-read playlist-modify-public playlist-modify-private'

        state = generate_random_string(16)
        request.session['spotify_state'] = state

        authorize_url = 'https://accounts.spotify.com/authorize'
        login_url = f"{authorize_url}?" + \
                    f"response_type=code&" + \
                    f"client_id={client_id}&" + \
                    f"scope={scope}&" + \
                    f"redirect_uri={redirect_uri}&" + \
                    f"state={state}"

        return JsonResponse({"login_url": login_url, "state": state})

class SpotifyCallbackView(APIView):
    def get(self, request):
        # Handle callback from Spotify OAuth
        code = request.GET.get('code')
        state = request.GET.get('state')

        print(request)
        if True:
            token_url = 'https://accounts.spotify.com/api/token'
            client_id = 'e2d12b171e824b4ba99f26afada7b99a'  # Replace with your Spotify client ID
            client_secret = 'c50ccb5a9bd14d628bbde1ea9198a441'  # Replace with your Spotify client secret
            redirect_uri = 'http://localhost:3000/signup'  # Replace with your redirect URI

            payload = {
                'code': code,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
            headers = {
                'content-type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic ' + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
            }

            try:
                response = requests.post(token_url, data=payload, headers=headers)
                if response.ok:
                    data = response.json()
                    access_token = data.get('access_token')
                    refresh_token = data.get('refresh_token')
                    # You can store or process the access token and refresh token here
                    return JsonResponse({'access_token': access_token, 'refresh_token': refresh_token})
                else:
                    return JsonResponse({'error': 'Failed to authenticate with Spotify'}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)


class SpotifyDataView(APIView):
    def post(self, request):
        access_token = request.data.get('access_token')
        user_id = request.data.get('user_id')
        name = request.data.get("name")
        mood = request.data.get("mood")

        if not access_token:
            return Response({'error': 'Access token is missing'}, status=status.HTTP_400_BAD_REQUEST)

        headers = {
            'Authorization': 'Bearer ' + access_token
        }

        try:
            response = requests.get('https://api.spotify.com/v1/me/player/recently-played?limit=30', headers=headers)
            response_data = response.json()

            # Extract song details from response
            songs = []
            for item in response_data.get('items', []):
                track = item.get('track', {})
                song_name = track.get('name', '')
                artists = [artist.get('name', '') for artist in track.get('artists', [])]
                album_name = track.get('album', {}).get('name', '')
                song_url = track.get('external_urls', {}).get('spotify', '')

                song_info = {
                    'song_name': song_name,
                    'artists': artists,
                    'album_name': album_name,
                    'song_url': song_url,
                    'song_uri': track.get('uri', '')
                }
                songs.append(song_info)

            uris = recommend_songs(songs, mood)
            pl_data = create_spotify_playlist(access_token, user_id, name)
            add_tracks_to_playlist(access_token, pl_data[1], uris)
            return Response({'url': pl_data[0]})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MoviesAPIView(APIView):
    def post(self, request):
        mood = request.data.get("mood")
        output = recommend_movies(mood)
        return JsonResponse({"movies": output})
