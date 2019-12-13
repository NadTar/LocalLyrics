
import os, jinja2,  json, logging, urllib, webapp2, urllib2
from google.appengine.api import urlfetch

#external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                                                   extensions=['jinja2.ext.autoescape'], autoescape=True)


class Artist:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.wiki = "https://en.wikipedia.org/?curid=" + str(id)
    def __str__(self):
        return self.name + ", views:" + str(self.views)
    def setViewCount(self, count):
        self.views = count
    def setSpotifyData(self, data):
        self.spotify = data["external_urls"]["spotify"]
        logging.info("doop")
        self.views = data["followers"]["total"]
        self.genre = data["genres"][0]
        self.image = data["images"][2]["url"]

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def safeGet(url):
    try:
        return urllib2.urlopen(url)
    except urllib.URLError as e:
        if hasattr(e,"code"):
            logging.error("The server couldn't fulfill the request.")
            logging.error("Error code: ", e.code)
        elif hasattr(e,'reason'):
            logging.error("We failed to reach a server")
            logging.error("Reason: ", e.reason)
        return None

def getLocation(ip):
    access_token = '7b364bd1de664f'
    url = 'http://ipinfo.io/' + ip + "?token=" + access_token
    response = urlfetch.fetch(url)
    data = json.loads(response.content)
    return [data["city"], data["country"], data["country"]]

def getArtists(location, token,  groups=False):
    city = location[0]
    region = location[1]
    token = getSpotifyAuth()
    wikiendpoint = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": "Category:Musicians from " + city
    }
    if groups:
        params["cmtitle"] = "Category:Musical groups from " + city
    url = wikiendpoint + "?" + urllib.urlencode(params)
    logging.info(url)
    response = json.load(safeGet(url))
    print(pretty(response))
    if (len(response["query"]["categorymembers"]) == 0):
        params["cmtitle"] = params["cmtitle"] + ", " + region
        url = wikiendpoint + "?" + urllib.urlencode(params)
        print(url)
        response = json.load(safeGet(url))
        print(pretty(response))
    artistlist = []
    for a in response["query"]["categorymembers"]:
        artist = Artist(a["title"], a["pageid"])
        try:
            getSpotifyData(artist, token)
            logging.info("spotty")
        except:
            logging.info("dead")
            addviewCounts(artist)
        artistlist.append(artist)
    while "continue" in response:
        params["cmcontinue"] = response["continue"]["cmcontinue"]
        #print(params)
        url = wikiendpoint + "?" + urllib.urlencode(params)
        response = json.load(safeGet(url))
        print(pretty(response))
        for b in response["query"]["categorymembers"]:
            bartist = Artist(b["title"], b["pageid"])
            try:
                getSpotifyData(bartist, token)
            except:
                addviewCounts(bartist)
            artistlist.append(bartist)
    return artistlist




def addviewCounts(a):
    viewcounturl = "wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/" + a.name + "/monthly/20101101/20191201"
    # coding: utf-8
    #print(a.name)
    try:
        safe = safeGet("https://" + urllib.quote(viewcounturl))
        data = json.load(safe)
        length = len(data['items'])
        # print(data)
        # print(data[0]['views'])
        a.setViewCount(data['items'][length - 1]['views'])
    except:
        a.setViewCount(0)

def getSpotifyData(a, token):
    url = "https://api.spotify.com/v1/search?q=" + a.name + "&type=artist"
    req = urllib2.Request(url)
    req.add_header('Authorization', 'Bearer ' + token)
    print(req.get_full_url())
    resp = urllib2.urlopen(req)
    content = json.load(resp)
    data = content["artists"]["items"][0]
    s = resp.read()
    print(pretty(content))
    logging.info("asdadsaasd")
    print(pretty(data))
    print(data["external_urls"]["spotify"])
    print(data["genres"][0])
    print(data["images"][0]["url"])

    #print(s)
    logging.info("poop")
    params = {}
    params['q'] = a.name
    params['type'] = 'artist'
    headers = {'Authorization': 'Bearer '+ token}
    #response = urlfetch.fetch(url=url, method=urlfetch.GET, payload=urllib.urlencode(params), headers=headers)

    #logging.info(response.content)
    #response_dict = json.loads(response.content)
    #print(content["artists"]["items"][0])
    a.setSpotifyData(data)

def prepData(ip):
    location = getLocation(ip)
    token = getSpotifyAuth()
    alist = getArtists(location, token)
    blist = getArtists(location, token,  True)
    alist = alist + blist
    sortedArtists = sorted(alist, key=lambda a: a.views, reverse=True)
    #for x in sortedArtists:
        #print(x)
    data = {"location": location, "artists": sortedArtists}
    return data

def getSpotifyAuth():
    client_id = "648f138d454943578320929f43802d86"
    client_secret = "cbe4efe69a3e4f52ba683eb81c78364a"
    base = "Basic  NjQ4ZjEzOGQ0NTQ5NDM1NzgzMjA5MjlmNDM4MDJkODY6Y2JlNGVmZTY5YTNlNGY1MmJhNjgzZWI4MWM3ODM2NGE="
    params = {}
    #args['client_id'] = client_id
    #args["client_secret"] = client_secret

    params['grant_type'] = 'client_credentials'
    url = "https://accounts.spotify.com/api/token"
    headers = {'Authorization':base , 'content-type': 'application/x-www-form-urlencoded'}
    response = urlfetch.fetch(url, method=urlfetch.POST, payload=urllib.urlencode(params), headers=headers)
    response_dict = json.loads(response.content)
    logging.info(response_dict["access_token"])
    print(response_dict)
    return response_dict["access_token"]

#token = getSpotifyAuth()
#print(token)
#getLocation("122.8.55.42")
#getSpotifyData(Artist('Drake', '12312'), token)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        headers = self.request.headers
        logging.info(headers)
        ip = self.request.remote_addr
        logging.info("blah")
        logging.info(headers)
        data = prepData(ip)
        template = JINJA_ENVIRONMENT.get_template('maintemp.html')
        self.response.write(template.render(data))

class SearchHandler(webapp2.RequestHandler):
    def get(self):
        city = self.request.get('city')
        region = self.request.get('region')
        location = [city, region, "unavailable"]
        logging.info(city)
        logging.info(region)
        token = getSpotifyAuth()
        alist = getArtists(location, token)
        blist = getArtists(location, token,  True)
        alist = alist + blist
        sortedArtists = sorted(alist, key=lambda a: a.views, reverse=True)
        data = {"location": location, "artists": sortedArtists}
        template = JINJA_ENVIRONMENT.get_template('maintemp.html')
        self.response.write(template.render(data))


application = webapp2.WSGIApplication([('/searchresponse', SearchHandler), ('/', MainHandler)], debug=True)

#getSpotifyData(Artist("Drake", 1111))
#vurl = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/Tom%20Abbs/monthly/20191101/20191201"
#r = safeGet(vurl)
#j = json.load(r)
#x = "Tom Abbs"
#print(urllib.parse.quote(x))
#print(pretty(j))
#print(getLocation(external_ip))
#client_credentials_manager = SpotifyClientCredentials("648f138d454943578320929f43802d86", "da48d8aa17b049d9ab22256150511293")
#sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#print(pretty(results))
#print(token)
#print(external_ip)


