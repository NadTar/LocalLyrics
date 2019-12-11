import urllib.request, spotipy
from spotipy.oauth2 import SpotifyClientCredentials


external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
client_credentials_manager = SpotifyClientCredentials("648f138d454943578320929f43802d86", "da48d8aa17b049d9ab22256150511293")
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

results = sp.search(q='artist: Carrie Brownstein', type='artist')
print(results)

print(external_ip)


