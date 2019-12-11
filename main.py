import spotipy
import spotipy.oauth2 as oauth2
import  os, jinja2,  json, logging, urllib, urllib.request, urllib.parse
import ipinfo

external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

class Artist:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.wiki = "https://en.wikipedia.org/?curid=" + str(id)
    def __str__(self):
        return self.name + ", views:" + str(self.views)
    def setViewCount(self, count):
        self.views = count

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def safeGet(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.request.URLError as e:
        if hasattr(e,"code"):
            logging.error("The server couldn't fulfill the request.")
            logging.error("Error code: ", e.code)
        elif hasattr(e,'reason'):
            logging.error("We failed to reach a server")
            logging.error("Reason: ", e.reason)
        return None
def getLocation(ip):
    access_token = '7b364bd1de664f'
    handler = ipinfo.getHandler(access_token)
    details = handler.getDetails(ip)
    print(details.city)
    return [details.city, details.region, details.country]

def getArtists(location):
    city = location[0]
    region = location[1]
    country = location[2]
    wikiendpoint = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": "Category:Musicians from " + city
    }
    url = wikiendpoint + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    #print(url)
    response = json.load(safeGet(url))
    print(pretty(response))
    if (len(response["query"]["categorymembers"]) == 0):
        params["cmtitle"] = params["cmtitle"] + ", " + region
        url = wikiendpoint + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        print(url)
        response = json.load(safeGet(url))
        print(pretty(response))
    artistlist = []
    for a in response["query"]["categorymembers"]:
        artist = Artist(a["title"], a["pageid"])
        addviewCounts(artist)
        artistlist.append(artist)
    while "continue" in response:
        params["cmcontinue"] = response["continue"]["cmcontinue"]
        #print(params)
        url = wikiendpoint + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        response = json.load(safeGet(url))
        print(pretty(response))
        for b in response["query"]["categorymembers"]:
            bartist = Artist(b["title"], b["pageid"])
            addviewCounts(bartist)
            artistlist.append(bartist)
    sortedArtists = sorted(artistlist, key=lambda a: a.views, reverse=True)
    for x in sortedArtists:
        print(x)



def addviewCounts(a):
    viewcounturl = "wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/" + a.name + "/monthly/20101101/20191201"
    print(viewcounturl)
    try:
        safe = safeGet("https://" + urllib.parse.quote(viewcounturl))
        data = json.load(safe)
        length = len(data['items'])
        # print(data)
        # print(data[0]['views'])
        a.setViewCount(data['items'][length - 1]['views'])
    except:
        a.setViewCount(0)
getArtists(getLocation("192.206.151.131"))
#vurl = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/Tom%20Abbs/monthly/20191101/20191201"
#r = safeGet(vurl)
#j = json.load(r)
#x = "Tom Abbs"
#print(urllib.parse.quote(x))
#print(pretty(j))
#print(getLocation(external_ip))
#client_credentials_manager = SpotifyClientCredentials("648f138d454943578320929f43802d86", "da48d8aa17b049d9ab22256150511293")
#sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
client_id = "648f138d454943578320929f43802d86"
client_secret = "da48d8aa17b049d9ab22256150511293"
credentials = oauth2.SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret)

token = credentials.get_access_token()
spotify = spotipy.Spotify(auth=token)
results = spotify.search(q='artist: Drake', type='artist')


#print(pretty(results))
#print(token)
#print(external_ip)


