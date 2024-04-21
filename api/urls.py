from django.urls import path
from api import views
from api.views import SpotifyLoginView, SpotifyCallbackView, SpotifyDataView, MoviesAPIView

image_analysis = views.MoodDetectViewSet.as_view({
    'post': 'image_analysis'
})


urlpatterns = [
    path("post-image/", image_analysis),
    path('spotify-login/', SpotifyLoginView.as_view(), name='spotify-login'),
    path('spotify-callback/', SpotifyCallbackView.as_view(), name='spotify-callback'),
    path('spotify-data/', SpotifyDataView.as_view(), name='spotify-data'),
    path('movies/', MoviesAPIView.as_view(), name='movies'),
]
