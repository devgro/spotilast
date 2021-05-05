# Spotilast by Devan Grover (dsgrover@andrew.cmu.edu)

import requests, hashlib, json, spotipy, math, time
from spotipy.oauth2 import SpotifyOAuth
from cmu_112_graphics import *

##########################################
# Splash Screen Mode
##########################################
allSongs = []

# Screen (modal) framework taken from 112 website: http://www.cs.cmu.edu/~112/notes/notes-animations-part4.html
def splashScreenMode_redrawAll(app, canvas):
    font = "Helvetica 13"
    canvas.create_rectangle(0, 0, app.width, app.height, fill="#FFC0CB", outline="#FFC0CB")
    canvas.create_text(app.width/2, 50, text='Welcome to SpotiLast!', font="Helvetica 35 italic",
                        anchor="n")
    instructions = ("To begin, please enter your last.fm and spotify usernames ",
                    "as well as your Client ID and secret for spotify.",
                    "You can find this data on Spotify by visiting ", 
                    "https://developer.spotify.com/dashboard/applications", 
                    "Set your spotify redirect URI to https://www.google.com/",
                    " in app settings after creating an app in the dashboard","", " ",
                    "To search and refresh the graphs within SpotiLast, ",
                    "press enter", "Press up to load in test data", "")
    for i in range(0, len(instructions), 2):
        canvas.create_text(app.width/2, 150+25*i//2, text=instructions[i]+instructions[i+1], font=font)
  
    canvas.create_text(app.width/2, 300, anchor="ne", text=f"Last.fm username: ", font=font)
    canvas.create_rectangle(app.width/2, 295, 3*app.width/4+20, 325, outline="black", fill="white")
    canvas.create_text(app.width/2 +5, 325, anchor="sw", text=app.LASTFM_USER, font=font)

    canvas.create_text(app.width/2, 340, text=f"Spotify username: ", anchor="ne", font=font)
    canvas.create_rectangle(app.width/2, 335, 3*app.width/4+20, 365, outline="black", fill="white")
    canvas.create_text(app.width/2 +5, 365, anchor="sw", text=app.SPOTIFY_USER, font=font)

    canvas.create_text(app.width/2, 380, text=f"Spotify Client ID: ", anchor="ne", font=font)
    canvas.create_rectangle(app.width/2, 375, 3*app.width/4+20, 405, outline="black", fill="white")
    canvas.create_text(app.width/2 +5, 405, anchor="sw", text=app.SPOTIFY_KEY, font=font)

    canvas.create_text(app.width/2, 420, text=f"Spotify Client Secret: ", anchor="ne", font=font)
    canvas.create_rectangle(app.width/2, 415, 3*app.width/4+20, 445, outline="black", fill="white")
    canvas.create_text(app.width/2 +5, 445, anchor="sw", text=app.SPOTIFY_SECRET, font=font)

    canvas.create_rectangle(7*app.width/16, 550, 9*app.width/16, 600, fill="#FFA8B7", outline="#FFA8B7")
    canvas.create_text(app.width/2, 575, text="Continue", font="Helvetica 20")

def mouseInBox(x, y, x1, y1, x2, y2): # Helper function to check if the mouse coordinates are in a box
    if(x <= x2 and x >= x1):
        if(y >= y1 and y <= y2):
            return True
    return False

def splashScreenMode_keyPressed(app, event):
    key = event.key
    if(key == "Up" or key == "up"): # Test case
        app.LASTFM_USER, app.LASTFM_KEY= "jonahliu", "45be5b99eb4c52bf0bf2175fdf56b820"
        app.SPOTIFY_USER, app.SPOTIFY_KEY, app.SPOTIFY_SECRET = "devg1", "ce96c423a54744b9844950a4382874ca", "69c65f35deeb44349f87d385662ecb57"
        app.mode="searchMode"
    if(len(key) == 1 or key == "backspace" or key == "Backspace"):
        if(app.currentlySelectedBox == "lastUser"):
            if(len(key) == 1):
                app.LASTFM_USER += key
            else:
                app.LASTFM_USER = app.LASTFM_USER[:-1]
        if(app.currentlySelectedBox == "lastAPI"):
            if(len(key) == 1):
                app.LASTFM_KEY += key
            else:
                app.LASTFM_KEY = app.LASTFM_KEY[:-1]
        if(app.currentlySelectedBox == "spotUser"):
            if(len(key) == 1):
                app.SPOTIFY_USER += key
            else:
                app.SPOTIFY_USER = app.SPOTIFY_USER[:-1]
        if(app.currentlySelectedBox == "spotAPI"):
            if(len(key) == 1):
                app.SPOTIFY_KEY += key
            else:
                app.SPOTIFY_KEY = app.SPOTIFY_KEY[:-1]
        if(app.currentlySelectedBox == "spotSecret"):
            if(len(key) == 1):
                app.SPOTIFY_SECRET += key
            else:
                app.SPOTIFY_SECRET = app.SPOTIFY_SECRET[:-1]
    
def splashScreenMode_mousePressed(app, event):
    x, y = event.x, event.y
    if(mouseInBox(x, y, app.width/2, 295, 3*app.width/4, 325,)):
        app.currentlySelectedBox = "lastUser"
    elif(mouseInBox(x, y, app.width/2, 335, 3*app.width/4, 365)):
        app.currentlySelectedBox = "spotUser"
    elif(mouseInBox(x, y, app.width/2, 375, 3*app.width/4, 405)):
        app.currentlySelectedBox = "spotAPI"
    elif(mouseInBox(x, y, app.width/2, 415, 3*app.width/4, 445)):
        app.currentlySelectedBox = "spotSecret"
    else:
        app.currentlySelectedBox = ""

    if(mouseInBox(x, y, 7*app.width/16, 550, 9*app.width/16, 600)):
        if(app.LASTFM_USER != "" and app.LASTFM_KEY != "" and app.SPOTIFY_USER != "" and app.SPOTIFY_KEY != "" and app.SPOTIFY_SECRET != ""):
            app.mode = "loadingDataMode"
            getData(app)

    if(app.SPOTIFY_SECRET != None and app.SPOTIFY_SECRET != ""):
        if(event.y >= 550 and event.y <= 600):
            if(event.x >=app.width/3 and event.x <= app.width/3 + app.width/9):
                app.mode = "loadingDataMode"
                getData(app)
            elif(event.x >= 2*app.width/3 - app.width/9 and event.x <= 2*app.width/3):
                appStarted(app)

##########################################
# Loading Data Mode
##########################################

def loadingDataMode_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill="#FFA8B7", 
                            outline="#FFA8B7")
    if(not app.loaded):
        canvas.create_text(app.width/2, 100, font="Helvetica 26 bold",
                        text="Loading...")
    else:
        canvas.create_text(app.width/2, 100, font="Helvetica 26 bold",
                        text="Loaded")
    pass

def getData(app): # Gets last.fm user data and stores them into 2 json files
    allSongs = []
    if(app.runGetData):
        if(f"{app.LASTFM_USER}_songs.json" in os.listdir()):
            with open(f"{app.LASTFM_USER}_songs.json", "r") as fp:
                allSongs = json.load(fp)
            if(allSongs[0]==None or allSongs[0].get("date") == None):
                lastDate = allSongs[1].get("date").get("uts")
            else:
                lastDate = allSongs[0].get("date").get("uts")
            getTrackUrl = f"?method=user.getrecenttracks&user={app.LASTFM_USER}&api_key={app.LASTFM_KEY}&limit=200&from={int(lastDate)+1}&format=json"
            getTrackRequest = requests.get(app.LASTFM_URL+getTrackUrl)
            request = getTrackRequest.json()
            newsongs = []
            totalPages = request.get("recenttracks").get("@attr").get("totalPages")
            print(totalPages)
            for i in range(1,int(totalPages)+1):
                getTrackUrl = f"?method=user.getrecenttracks&user={app.LASTFM_USER}&api_key={app.LASTFM_KEY}&limit=200&from={int(lastDate)+1}&page={i}&format=json"
                getTrackRequest = requests.get(app.LASTFM_URL+getTrackUrl)
                request = getTrackRequest.json()
                newsongs = newsongs + request.get("recenttracks").get("track")
                allSongs = newsongs + allSongs
            with open(f"{app.LASTFM_USER}_songs.json", "w") as fp:
                json.dump(allSongs, fp, indent=1)
        else:
            getTrackUrl = f"?method=user.getrecenttracks&user={app.LASTFM_USER}&api_key={app.LASTFM_KEY}&limit=200&format=json"
            getTrackRequest = requests.get(app.LASTFM_URL+getTrackUrl)
            request = getTrackRequest.json()
            newsongs = []
            totalPages = request.get("recenttracks").get("@attr").get("totalPages")
            print(totalPages)
            for i in range(1,int(totalPages)+1):
                if(i%10 == 0): print(i)
                getTrackUrl = f"?method=user.getrecenttracks&user={app.LASTFM_USER}&api_key={app.LASTFM_KEY}&limit=200&page={i}&format=json"
                getTrackRequest = requests.get(app.LASTFM_URL+getTrackUrl)
                request = getTrackRequest.json()
                allSongs = allSongs + request.get("recenttracks").get("track")
            with open(f"{app.LASTFM_USER}_songs.json", "w") as fp:
                json.dump(allSongs, fp, indent=3)
        getTrackUrl = f"?method=user.gettoptracks&user={app.LASTFM_USER}&period=overall&api_key={app.LASTFM_KEY}&limit=200&format=json"
        getTrackRequest = requests.get(app.LASTFM_URL+getTrackUrl)
        request = getTrackRequest.json()
        print(request)
        songs = []
        totalPages = request["toptracks"]["@attr"]["totalPages"]
        for i in range(1,int(totalPages)+1):
            if(i%10 == 0): print(i)
            getTrackUrl = f"?method=user.gettoptracks&user={app.LASTFM_USER}&period=overall&api_key={app.LASTFM_KEY}&limit=200&page={i}&format=json"
            getTrackRequest = requests.get(app.LASTFM_URL+getTrackUrl)
            request = getTrackRequest.json()
            songs = songs + request["toptracks"]["track"]
        for i in songs:
            i["album"] = ""
            for p in allSongs:
                if(i.get("name") == p.get("name") and i.get("artist").get("name") == p.get("artist").get("#text")):
                    i["album"] = p.get("album").get("#text")
                    break
        with open(f"{app.LASTFM_USER}_topSongs.json", "w") as fp:
            json.dump(songs, fp, indent=3)
        app.loaded = True
            
def loadingDataMode_timerFired(app):
    app.runGetData = True
    if(app.runGetData and not app.getDataTracker):
        app.getDataTracker = True
        getData(app)
    if(app.loaded):
        app.mode = "searchMode"

##########################################
# Search Mode (Album, Artist, Plays, Duration)
##########################################

def searchMode_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill="#FFA8B7", 
                            outline="#FFA8B7")
    canvas.create_rectangle(0, app.height/6, app.width, app.height, fill="#FFC0CB",
                            outline="#FFC0CB")
    canvas.create_rectangle(0, 0, app.width/4, app.height/6, fill="#FFC0CB",
                            outline="#FFC0CB")
    canvas.create_line(app.width/2, 0, app.width/2, app.height/6, fill="#FFC0CB")
    canvas.create_line(3*app.width/4, 0, 3*app.width/4, app.height/6, fill="#FFC0CB")
    canvas.create_text(app.width/8, app.height/12, text="Search", font="Helvetica 35")
    canvas.create_text(3*app.width/8, app.height/12, text="Graphs", font="Helvetica 35")
    canvas.create_text(5*app.width/8, app.height/12, text="Queries", font="Helvetica 35")
    canvas.create_text(7*app.width/8, app.height/12, text="Export", font="Helvetica 35")

    canvas.create_text(6*app.width/8, 5*app.height/20, text=f"Results: {len(app.results)}", anchor = "se")
    canvas.create_text(6*app.width/8 + 10, 5*app.height/20, text=f"Selected: {len(app.selectedSongs)}", anchor = "sw")
    canvas.create_rectangle(2*app.width/8, 5*app.height/20, 6*app.width/8, 6*app.height/20, fill="white")
    canvas.create_text(2*app.width/8, 5*app.height/20, anchor="sw", text="Song Title:", font="Helvetica 20")
    searchFont = f"Helvetica {str(app.searchQueryFontSize)}"
    canvas.create_text(2*app.width/8+2, 6*app.height/20, anchor="sw", text=app.titleQuery, font=searchFont)

    canvas.create_text(3*app.width/32, 7*app.height/20, anchor="sw", text="Album:")
    canvas.create_rectangle(3*app.width/32, 14*app.height/40, 8*app.width/32, 15*app.height/40, fill="white")
    canvas.create_text(3*app.width/32 +5, 15*app.height/40, anchor="sw", text=app.albumQuery)

    canvas.create_text(10*app.width/32, 7*app.height/20, anchor="sw", text="Artist:")
    canvas.create_rectangle(10*app.width/32, 14*app.height/40, 15*app.width/32, 15*app.height/40, fill="white")
    canvas.create_text(10*app.width/32 +5, 15*app.height/40, anchor="sw", text=app.artistQuery)

    canvas.create_text(17*app.width/32, 7*app.height/20, anchor="sw", text="Plays (>min, <max, >min and <max):")
    canvas.create_rectangle(17*app.width/32, 7*app.height/20, 22*app.width/32, 15*app.height/40, fill="white")
    canvas.create_text(17*app.width/32 +5, 15*app.height/40, anchor="sw", text=app.playsQuery)

    canvas.create_text(24*app.width/32, 7*app.height/20, anchor="sw", text="Length (>min, <max, >min and <max):")
    canvas.create_rectangle(24*app.width/32, 7*app.height/20, 29*app.width/32, 15*app.height/40, fill="white")
    canvas.create_text(24*app.width/32 +5, 15*app.height/40, anchor="sw", text=app.durationQuery)
    
    for i in range(app.searchPage*5, app.searchPage*5+5):
        if(i < len(app.results)):
            fill="black"
            if(app.results[i] in app.selectedSongs):
                fill="blue"
            if(len(app.results[i].get("name")) > 50):
                nam = app.results[i].get("name")[:50]
            else:
                nam = app.results[i].get("name")
            if(len(app.results[i].get("album")) > 50):
                alb = app.results[i].get("album")[:50]
            else:
                alb = app.results[i].get("album")
            if(len(app.results[i].get("artist").get("name")) > 40):
                artis = app.results[i].get("artist").get("name")[:40]
            else:
                artis = app.results[i].get("artist").get("name")
            canvas.create_text(10, (22+(i%5)*4)*app.height/40, text=nam, anchor="w", fill=fill, font="Helvetica 12")
            canvas.create_text(2.75*app.width/5, (22+(i%5)*4)*app.height/40, text=alb, anchor="w", font="Helvetica 12")
            canvas.create_text(1.5*app.width/5, (22+(i%5)*4)*app.height/40, text=artis, anchor="w", font="Helvetica 12")
            canvas.create_text(4.25*app.width/5, (22+(i%5)*4)*app.height/40, text=app.results[i].get("playcount"), anchor="e", font="Helvetica 12")
            tot = int(app.results[i].get("duration"))
            secs = tot%60
            mins = tot//60
            if(secs < 10):
                secs = f"0{secs}"
            canvas.create_text(4.5*app.width/5, (22+(i%5)*4)*app.height/40, text=f"{mins}:{secs}", anchor="w", font="Helvetica 12")
    canvas.create_polygon(app.width-40, app.height-30, app.width-20, app.height-30, app.width-30, app.height-17.321)
    canvas.create_polygon(app.width-40, 22*app.height/40+12.7, app.width-20, 22*app.height/40+12.7, app.width-30, 22*app.height/40)
    canvas.create_line(0,20*app.height/40, app.width, 20*app.height/40)
    canvas.create_line(0,24*app.height/40, app.width, 24*app.height/40)
    canvas.create_line(0,28*app.height/40, app.width, 28*app.height/40)
    canvas.create_line(0,32*app.height/40, app.width, 32*app.height/40)
    canvas.create_line(0,36*app.height/40, app.width, 36*app.height/40)
    canvas.create_text(10, 20*app.height/40, anchor="sw", text="Title:", font="Helvetica 18")
    canvas.create_text(2.75*app.width/5, 20*app.height/40, anchor="sw", text="Album", font="Helvetica 18")
    canvas.create_text(1.5*app.width/5, 20*app.height/40, anchor="sw", text="Artist", font="Helvetica 18")
    canvas.create_text(4.25*app.width/5, 20*app.height/40, anchor="se", text="Plays", font="Helvetica 18")
    canvas.create_text(4.5*app.width/5, 20*app.height/40, anchor="sw", text="Length", font="Helvetica 18")
    canvas.create_text(app.width/2, 16*app.height/40, anchor="n", font="Helvetica 12",
        text="Press enter to search. Plays and Length have to be formatted with >min, <max, or both with the word \"and\" in between")
    canvas.create_text(app.width/2, 16*app.height/40+18, anchor="n", font="Helvetica 12",
        text="Length is in seconds. Press = to select all search results, and - to clear your selection")

def searchMode_mousePressed(app, event):
    x, y = event.x, event.y
    if(y >= 0 and y <= app.height/6):
        if(x >= app.width/4 and x <= 2* app.width/4):
            app.mode = "pieChartMode"
        elif(x >= 2 * app.width/4 and x <= 3 * app.width/4):
            app.mode = "queryMode"
        elif(x >= app.width/4):
            app.mode = "exportMode"
    if(mouseInBox(x, y, 3*app.width/32, 14*app.height/40, 8*app.width/32, 15*app.height/40)):
        app.currentlySelectedBox = "album"
    elif(mouseInBox(x, y, 10*app.width/32, 14*app.height/40, 15*app.width/32, 15*app.height/40)):
        app.currentlySelectedBox = "artist"
    elif(mouseInBox(x, y, 17*app.width/32, 7*app.height/20, 22*app.width/32, 15*app.height/40)):
        app.currentlySelectedBox = "plays"
    elif(mouseInBox(x, y, 24*app.width/32, 7*app.height/20, 29*app.width/32, 15*app.height/40)):
        app.currentlySelectedBox = "duration"
    elif(mouseInBox(x, y, 2*app.width/8, 5*app.height/20, 6*app.width/8, 6*app.height/20)):
        app.currentlySelectedBox = "title"
    elif(mouseInBox(x, y, app.width-40, app.height-30, app.width-20, app.height-17.321)):
        if(app.searchPage < math.ceil(len(app.results)/5)-1):
            app.searchPage += 1
    elif(mouseInBox(x, y, app.width-40, 22*app.height/40, app.width-20, 22*app.height/40+12.7)):
        if(app.searchPage > 0):
            app.searchPage -= 1
            
    # Algorithm for sorting list of dicts from https://www.geeksforgeeks.org/ways-sort-list-dictionaries-values-python-using-lambda-function/
    if(mouseInBox(x, y, 10, app.height/2-30, 40, app.height/2)):
        if(app.resultsLastSorted[1] == "name"):
            if(app.resultsLastSorted[0] == 0):
                app.resultsLastSorted = (1, "name")
                app.results = sorted(app.results, key=lambda k: k["name"].lower(), reverse=True)
            else:
                app.resultsLastSorted = (0, "name")
                app.results = sorted(app.results, key=lambda k: k["name"].lower(), reverse=False)
        else:
            app.resultsLastSorted = (0, "name")
            app.results = sorted(app.results, key=lambda k: k["name"].lower(), reverse = False)
    elif(mouseInBox(x, y, 1.5*app.width/5, app.height/2-30, 1.5*app.width/5+60, app.height/2)):
        if(app.resultsLastSorted[1] == "artist"):
            if(app.resultsLastSorted[0] == 0):
                app.resultsLastSorted = (1, "artist")
                app.results = sorted(app.results, key=lambda k: k["artist"]["name"].lower(), reverse=True)
            else:
                app.resultsLastSorted = (0, "artist")
                app.results = sorted(app.results, key=lambda k: k["artist"]["name"].lower(), reverse=False)
        else:
            app.resultsLastSorted = (0, "artist")
            app.results = sorted(app.results, key=lambda k: k["artist"]["name"].lower(), reverse = False)
    elif(mouseInBox(x, y, 2.75*app.width/5, app.height/2-30, 2.75*app.width/5+70, app.height/2)):
        if(app.resultsLastSorted[1] == "album"):
            if(app.resultsLastSorted[0] == 0):
                app.resultsLastSorted = (1, "album")
                app.results = sorted(app.results, key=lambda k: k["album"].lower(), reverse=True)
            else:
                app.resultsLastSorted = (0, "album")
                app.results = sorted(app.results, key=lambda k: k["album"].lower(), reverse=False)
        else:
            app.resultsLastSorted = (0, "album")
            app.results = sorted(app.results, key=lambda k: k["album"].lower(), reverse = False)
    elif(mouseInBox(x, y, 4.25*app.width/5-65, app.height/2-30, 4.25*app.width/5, app.height/2)):
        if(app.resultsLastSorted[1] == "playcount"):
            if(app.resultsLastSorted[0] == 0):
                app.resultsLastSorted = (1, "playcount")
                app.results = sorted(app.results, key=lambda k: int(k["playcount"]), reverse=True)
            else:
                app.resultsLastSorted = (0, "playcount")
                app.results = sorted(app.results, key=lambda k: int(k["playcount"]), reverse=False)
        else:
            app.resultsLastSorted = (0, "playcount")
            app.results = sorted(app.results, key=lambda k: int(k["playcount"]), reverse = False)
    elif(mouseInBox(x, y, 4.5*app.width/5, app.height/2-30, 4.5*app.width/5 +75, app.height/2)):
        if(app.resultsLastSorted[1] == "duration"):
            if(app.resultsLastSorted[0] == 0):
                app.resultsLastSorted = (1, "duration")
                app.results = sorted(app.results, key=lambda k: int(k["duration"]), reverse=True)
            else:
                app.resultsLastSorted = (0, "duration")
                app.results = sorted(app.results, key=lambda k: int(k["duration"]), reverse=False)
        else:
            app.resultsLastSorted = (0, "duration")
            app.results = sorted(app.results, key=lambda k: int(k["duration"]), reverse = False)

    try:
        if(mouseInBox(x, y, 0, 20*app.height/40, app.width - 45, 24*app.height/40)):
            if(app.results[app.searchPage*5] in app.selectedSongs):
                app.selectedSongs.remove(app.results[app.searchPage*5])
            else:
                app.selectedSongs.append(app.results[app.searchPage*5])
        elif(mouseInBox(x, y, 0, 24*app.height/40, app.width - 45, 28*app.height/40)):
            if(app.results[app.searchPage*5 + 1] in app.selectedSongs):
                app.selectedSongs.remove(app.results[app.searchPage*5 + 1])
            else:
                app.selectedSongs.append(app.results[app.searchPage*5 + 1])
        elif(mouseInBox(x, y, 0, 28*app.height/40, app.width - 45, 32*app.height/40)):
            if(app.results[app.searchPage*5 + 2] in app.selectedSongs):
                app.selectedSongs.remove(app.results[app.searchPage*5 + 2])
            else:
                app.selectedSongs.append(app.results[app.searchPage*5 + 2])
        elif(mouseInBox(x, y, 0, 32*app.height/40, app.width - 45, 36*app.height/40)):
            if(app.results[app.searchPage*5 + 3] in app.selectedSongs):
                app.selectedSongs.remove(app.results[app.searchPage*5 + 3])
            else:
                app.selectedSongs.append(app.results[app.searchPage*5 + 3])
        elif(mouseInBox(x, y, 0, 36*app.height/40, app.width - 45, 40*app.height/40)):
            if(app.results[app.searchPage*5 + 4] in app.selectedSongs):
                app.selectedSongs.remove(app.results[app.searchPage*5 + 4])
            else:
                app.selectedSongs.append(app.results[app.searchPage*5 + 4])
    except:
        pass
    
    

def searchMode_keyPressed(app, event):
    key = event.key
    if(key == "="):
        for i in app.results:
            if(i not in app.selectedSongs):
                app.selectedSongs.append(i)
    if(key == "-"):
        app.selectedSongs = []
    if(len(key) == 1 or key == "backspace" or key == "Backspace" or key == "space" or key == "Space"):
        if(app.currentlySelectedBox == "album"):
            if(len(key) == 1 and len(app.albumQuery) < 27):
                app.albumQuery += key
            elif(key == "space" or key == "Space"):
                app.albumQuery += " "
            elif(key == "Backspace" or key == "space"):
                app.albumQuery = app.albumQuery[:-1]
        if(app.currentlySelectedBox == "artist"):
            if(len(key) == 1 and len(app.artistQuery) < 27):
                app.artistQuery += key
            elif(key == "space" or key == "Space"):
                app.artistQuery += " "
            elif(key == "Backspace" or key == "space"):
                app.artistQuery = app.artistQuery[:-1]
        if(app.currentlySelectedBox == "plays"):
            if(len(key) == 1 and len(app.playsQuery) < 27):
                app.playsQuery += key
            elif(key == "space" or key == "Space"):
                app.playsQuery += " "
            elif(key == "Backspace" or key == "backspace"):
                app.playsQuery = app.playsQuery[:-1]
        if(app.currentlySelectedBox == "duration"):
            if(len(key) == 1 and len(app.durationQuery) < 27):
                app.durationQuery += key
            elif(key == "space" or key == "Space"):
                app.durationQuery += " "
            elif(key == "Backspace" or key == "backspace"):
                app.durationQuery = app.durationQuery[:-1]
        if(app.currentlySelectedBox == "title"):
            if(len(key) == 1 and len(app.titleQuery) < 40):
                app.titleQuery += key
            elif(key == "space" or key == "Space"):
                app.titleQuery += " "
            elif(key == "Backspace" or key == "backspace"):
                app.titleQuery = app.titleQuery[:-1]
    if(key == "enter" or key == "Enter"):
        app.searchPage = 0
        search(app)

def search(app):
    app.results = []
    date = True
    fields = {"title":app.titleQuery, "artist":app.artistQuery,"album":app.albumQuery,
                "duration":app.durationQuery, "plays":app.playsQuery, "date":app.dateQuery}
    tracker = False
    for key in fields:
        if fields.get(key) != "":
            tracker = True
    if(not tracker): return
    
    if(fields.get("date") == ""): date = False
    pops = []
    for key in fields:
        if(fields.get(key) == ""):
            pops.append(key)
    for key in pops:
        fields.pop(key)
    if(date == False):
        with open(f"{app.LASTFM_USER}_topSongs.json", "r") as fp:
            topSongs = json.load(fp)
        for i in topSongs:
            isSong = True
            for field in fields:
                if(field == "title"):
                    if(not(fields.get(field).lower() in i.get("name").lower())):
                        isSong = False
                if(field == "artist"):
                    if(not(fields.get(field).lower() in i.get("artist").get("name").lower())):
                        isSong = False
                if(field == "album"):
                    if(not(fields.get(field).lower() in i.get("album").lower())):
                        isSong = False
                if(field == "duration"):
                    high, low = 1000000, 0
                    arr = fields.get(field).split(" ")
                    for p in arr:
                        if(p[0] == ">"):
                            low = int(p[1:])
                        elif(p[0] == "<"):
                            high = int(p[1:])
                    if(not(low < int(i.get("duration")) and high > int(i.get("duration")))):
                        isSong = False
                if(field == "plays"):
                    high, low = 1000000, 0
                    arr = fields.get(field).split(" ")
                    for p in arr:
                        if(p[0] == ">"):
                            low = int(p[1:])
                        elif(p[0] == "<"):
                            high = int(p[1:])
                    if(not(low < int(i.get("playcount")) and high > int(i.get("playcount")))):
                        isSong = False
                    print(field, p, low, high, isSong)
            if(isSong):
                app.results.append(i)
        print(len(app.results))


##########################################
# Pie Chart Mode
##########################################

def pieChartMode_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill="#FFA8B7", 
                            outline="#FFA8B7")
    canvas.create_rectangle(0, app.height/6, app.width, app.height, fill="#FFC0CB",
                            outline="#FFC0CB")
    canvas.create_rectangle(app.width/4, 0, app.width/2, app.height/6, fill="#FFC0CB",
                            outline="#FFC0CB")
    # canvas.create_line(app.width/4, 0, app.width/2, app.height/6, fill="#FFC0CB")
    canvas.create_line(3*app.width/4, 0, 3*app.width/4, app.height/6, fill="#FFC0CB")
    canvas.create_text(app.width/8, app.height/12, text="Search", font="Helvetica 35")
    canvas.create_text(3*app.width/8, app.height/12, text="Graphs", font="Helvetica 35")
    canvas.create_text(5*app.width/8, app.height/12, text="Queries", font="Helvetica 35")
    canvas.create_text(7*app.width/8, app.height/12, text="Export", font="Helvetica 35")
    canvas.create_rectangle(42*app.width/100,app.height/6+20, 58*app.width/100, app.height/6+80, fill="#FFA8B7", outline="#FFA8B7")
    canvas.create_rectangle(67*app.width/100,app.height/6+20, 83*app.width/100, app.height/6+80, fill="#FFA8B7", outline="#FFA8B7")
    canvas.create_text(app.width/4, app.height/6 + 50, text="Pie Chart", font="Helvetica 20")
    canvas.create_text(2*app.width/4, app.height/6 + 50, text="Bar Graph", font="Helvetica 20")
    canvas.create_text(3*app.width/4, app.height/6 + 50, text="Line Graph", font="Helvetica 20")
    canvas.create_text(6*app.width/100, app.height/6 + 120, text="Top:", anchor="se",font="Helvetica 18")
    canvas.create_rectangle(7*app.width/100, app.height/6 + 90, 12*app.width/100, app.height/6 + 120, fill="white")
    canvas.create_text(19*app.width/200, app.height/6 + 125, anchor="n", text="(2-25)")
    canvas.create_text(7*app.width/100 + 7, app.height/6 + 120, anchor="sw", font="Helvetica 15", text=app.pieSettings[0])
    canvas.create_text(15*app.width/100, app.height/6+120, text="Type:", anchor="sw", font="Helvetica 18")
    if(app.pieSettings[1] == "songs"):
        canvas.create_rectangle(28*app.width/100, app.height/6 + 90, 34*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(35*app.width/100, app.height/6 + 90, 41*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.pieSettings[1] == "artists"):
        canvas.create_rectangle(21*app.width/100, app.height/6 + 90, 27*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(35*app.width/100, app.height/6 + 90, 41*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.pieSettings[1] == "albums"):
        canvas.create_rectangle(21*app.width/100, app.height/6 + 90, 27*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(28*app.width/100, app.height/6 + 90, 34*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    canvas.create_text(24*app.width/100, app.height/6+107, text="Songs", font="Helvetica 15", anchor="center")
    canvas.create_text(31*app.width/100, app.height/6+107, text="Artists", font="Helvetica 15", anchor="center")
    canvas.create_text(38*app.width/100, app.height/6+107, text="Albums", font="Helvetica 15", anchor="center")


    if(app.pieSettings[2] == "7day"):
        canvas.create_rectangle(58.5*app.width/100, app.height/6 + 90, 66*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(67*app.width/100, app.height/6 + 90, 75*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(76*app.width/100, app.height/6 + 90, 84*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(85*app.width/100, app.height/6 + 90, 91*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(92*app.width/100, app.height/6 + 90, 98*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.pieSettings[2] == "1month"):
        canvas.create_rectangle(50.5*app.width/100, app.height/6 + 90, 57.5*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(67*app.width/100, app.height/6 + 90, 75*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(76*app.width/100, app.height/6 + 90, 84*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(85*app.width/100, app.height/6 + 90, 91*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(92*app.width/100, app.height/6 + 90, 98*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.pieSettings[2] == "3month"):
        canvas.create_rectangle(50.5*app.width/100, app.height/6 + 90, 57.5*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(58.5*app.width/100, app.height/6 + 90, 66*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(76*app.width/100, app.height/6 + 90, 84*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(85*app.width/100, app.height/6 + 90, 91*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(92*app.width/100, app.height/6 + 90, 98*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.pieSettings[2] == "6month"):
        canvas.create_rectangle(50.5*app.width/100, app.height/6 + 90, 57.5*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(58.5*app.width/100, app.height/6 + 90, 66*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(67*app.width/100, app.height/6 + 90, 75*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(85*app.width/100, app.height/6 + 90, 91*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(92*app.width/100, app.height/6 + 90, 98*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.pieSettings[2] == "12month"):
        canvas.create_rectangle(50.5*app.width/100, app.height/6 + 90, 57.5*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(58.5*app.width/100, app.height/6 + 90, 66*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(67*app.width/100, app.height/6 + 90, 75*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(76*app.width/100, app.height/6 + 90, 84*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(92*app.width/100, app.height/6 + 90, 98*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.pieSettings[2] == "overall"):
        canvas.create_rectangle(50.5*app.width/100, app.height/6 + 90, 57.5*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(58.5*app.width/100, app.height/6 + 90, 66*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(67*app.width/100, app.height/6 + 90, 75*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(76*app.width/100, app.height/6 + 90, 84*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(85*app.width/100, app.height/6 + 90, 91*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    canvas.create_text(44*app.width/100, app.height/6 + 120, text="Time:", anchor="sw", font="Helvetica 18")
    canvas.create_text(54*app.width/100, app.height/6 + 107, text="1 Week", font="Helvetica 15", anchor="center")
    canvas.create_text(62*app.width/100, app.height/6 + 107, text="1 Month", font="Helvetica 15")
    canvas.create_text(71*app.width/100, app.height/6 + 107, text="3 Months", font="Helvetica 15")
    canvas.create_text(80*app.width/100, app.height/6 + 107, text="6 Months", font="Helvetica 15")
    canvas.create_text(88*app.width/100, app.height/6 + 107, text="1 Year", font="Helvetica 15")
    canvas.create_text(95*app.width/100, app.height/6 + 107, text="Overall", font="Helvetica 15")
    if(app.drawPie):
        drawPieChart(app, canvas)


def pieChartMode_mousePressed(app, event): 
    x, y = event.x, event.y
    if(y >= 0 and y <= app.height/6):
        if(x >= 2 * app.width/4 and x <= 3 * app.width/4):
            app.mode = "queryMode"
        elif(x >= 0 and x <= app.width/4):
            app.mode = "searchMode"
        elif(x >= app.width/4):
            app.mode = "exportMode"
    if(mouseInBox(x, y, 42*app.width/100,app.height/6+20, 58*app.width/100, app.height/6+80)):
        app.drawPie = False
        app.mode="barGraphMode"
    if(mouseInBox(x, y, 67*app.width/100,app.height/6+20, 83*app.width/100, app.height/6+80)):
        app.drawPie = False
        app.mode="lineGraphMode"
    if(mouseInBox(x, y, 7*app.width/100, app.height/6 + 90, 12*app.width/100, app.height/6 + 120)):
        app.selectedPie = True
    else:
        app.selectedPie = False
    if(mouseInBox(x, y,28*app.width/100, app.height/6 + 90, 34*app.width/100, app.height/6 + 125)):
        app.pieSettings = (app.pieSettings[0], "artists", app.pieSettings[2])
    elif(mouseInBox(x, y,35*app.width/100, app.height/6 + 90, 41*app.width/100, app.height/6 + 125)):
        app.pieSettings = (app.pieSettings[0], "albums", app.pieSettings[2])
    elif(mouseInBox(x, y,21*app.width/100, app.height/6 + 90, 27*app.width/100, app.height/6 + 125)):
        app.pieSettings = (app.pieSettings[0], "songs", app.pieSettings[2])
    if(mouseInBox(x, y,50.5*app.width/100, app.height/6 + 90, 57.5*app.width/100, app.height/6 + 125)):
        app.pieSettings = (app.pieSettings[0], app.pieSettings[1], "7day")
    if(mouseInBox(x, y,58.5*app.width/100, app.height/6 + 90, 66*app.width/100, app.height/6 + 125,)):
        app.pieSettings = (app.pieSettings[0], app.pieSettings[1], "1month")
    if(mouseInBox(x, y,67*app.width/100, app.height/6 + 90, 75*app.width/100, app.height/6 + 125)):
        app.pieSettings = (app.pieSettings[0], app.pieSettings[1], "3month")
    if(mouseInBox(x, y,76*app.width/100, app.height/6 + 90, 84*app.width/100, app.height/6 + 125)):
        app.pieSettings = (app.pieSettings[0], app.pieSettings[1], "6month")
    if(mouseInBox(x, y,85*app.width/100, app.height/6 + 90, 91*app.width/100, app.height/6 + 125)):
        app.pieSettings = (app.pieSettings[0], app.pieSettings[1], "12month")
    if(mouseInBox(x, y,92*app.width/100, app.height/6 + 90, 98*app.width/100, app.height/6 + 125)):
        app.pieSettings = (app.pieSettings[0], app.pieSettings[1], "overall")


def pieChartMode_keyPressed(app, event):
    key = event.key
    print(app.pieSettings)
    if(len(app.pieSettings[0]) == 0 and key == "0"):
        return
    if(app.selectedPie):
        if(key.isnumeric() or key == "backspace" or key == "Backspace"):
            if(key.isnumeric() and int(app.pieSettings[0] + key) < 26):
                app.pieSettings = (app.pieSettings[0]+key, app.pieSettings[1], app.pieSettings[2])
            elif(key == "backspace" or key == "Backspace"):
                app.pieSettings = (app.pieSettings[0][:-1], app.pieSettings[1], app.pieSettings[2])
    if(key == "enter" or key == "Enter" and app.pieSettings[0] != "" and int(app.pieSettings[0]) > 1):
        getPieData(app)
    

def getPieData(app):
    app.encodedPieData = {}
    num, tipe,  times = app.pieSettings
    if(tipe == "songs"):
        getSongUrl = f"?method=user.gettoptracks&user={app.LASTFM_USER}&period={ times}&api_key={app.LASTFM_KEY}&limit={num}&format=json"
        getSongRequest = requests.get(app.LASTFM_URL+getSongUrl)
        request = getSongRequest.json()
        print(json.dumps(request, indent=1))
        app.pieData = request["toptracks"]["track"]
    elif(tipe == "artists"):
        getArtistUrl = f"?method=user.gettopartists&user={app.LASTFM_USER}&period={ times}&api_key={app.LASTFM_KEY}&limit={num}&format=json"
        getArtistRequest = requests.get(app.LASTFM_URL+getArtistUrl)
        request = getArtistRequest.json()
        print(json.dumps(request, indent=1))
        app.pieData = request["topartists"]["artist"]
    elif(tipe == "albums"):
        getAlbumUrl = f"?method=user.gettopalbums&user={app.LASTFM_USER}&period={ times}&api_key={app.LASTFM_KEY}&limit={num}&format=json"
        getAlbumRequest = requests.get(app.LASTFM_URL+getAlbumUrl)
        request = getAlbumRequest.json()
        print(json.dumps(request, indent=1))
        app.pieData = request["topalbums"]["album"]
    totalCount = 0
    for i in app.pieData:
        totalCount += int(i.get("playcount"))
    for i in app.pieData:
        app.encodedPieData[i.get("name")] = (int(i.get("playcount"))/totalCount) * 360
    print(app.encodedPieData)
    app.drawPie = True


def drawPieChart(app, canvas):
    angleCounter = 0
    count = 0
    for key in app.encodedPieData:
        canvas.create_arc(30, app.height/3+20, 30+2*app.height/3-30, 
        app.height/3 +20+2*app.height/3-30, style="pieslice", start=angleCounter, 
        extent=app.encodedPieData.get(key), width=1, fill=app.colors[count])
        #print(key, app.colors[count])
        angleCounter += app.encodedPieData.get(key)
        canvas.create_rectangle(app.width/2 + (count//13)*app.width/4, app.height/3 + 20 + (count%13)*app.width/36, 
                                app.width/2 + (count//13)*app.width/4 + 20, app.height/3 + 20 + (count%13)*app.width/36 + 20,
                                fill=app.colors[count], outline=app.colors[count])
        canvas.create_text(app.width/2 + (count//13)*app.width/4 + 35, app.height/3 + 20 + (count%13)*app.width/36 + 20,
                            anchor="sw", text=key)
        count += 1

##########################################
# Bar Graph Mode
##########################################

def barGraphMode_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill="#FFA8B7", 
                            outline="#FFA8B7")
    canvas.create_rectangle(0, app.height/6, app.width, app.height, fill="#FFC0CB",
                            outline="#FFC0CB")
    canvas.create_rectangle(app.width/4, 0, app.width/2, app.height/6, fill="#FFC0CB",
                            outline="#FFC0CB")
    # canvas.create_line(app.width/4, 0, app.width/2, app.height/6, fill="#FFC0CB")
    canvas.create_line(3*app.width/4, 0, 3*app.width/4, app.height/6, fill="#FFC0CB")
    canvas.create_text(app.width/8, app.height/12, text="Search", font="Helvetica 35")
    canvas.create_text(3*app.width/8, app.height/12, text="Graphs", font="Helvetica 35")
    canvas.create_text(5*app.width/8, app.height/12, text="Queries", font="Helvetica 35")
    canvas.create_text(7*app.width/8, app.height/12, text="Export", font="Helvetica 35")
    canvas.create_rectangle(17*app.width/100,app.height/6+20, 33*app.width/100, app.height/6+80, fill="#FFA8B7", outline="#FFA8B7")
    canvas.create_rectangle(67*app.width/100,app.height/6+20, 83*app.width/100, app.height/6+80, fill="#FFA8B7", outline="#FFA8B7")
    canvas.create_text(app.width/4, app.height/6 + 50, text="Pie Chart", font="Helvetica 20")
    canvas.create_text(2*app.width/4, app.height/6 + 50, text="Bar Graph", font="Helvetica 20")
    canvas.create_text(3*app.width/4, app.height/6 + 50, text="Line Graph", font="Helvetica 20")
    canvas.create_text(6*app.width/100, app.height/6 + 120, text="Top:", anchor="se",font="Helvetica 18")
    canvas.create_rectangle(7*app.width/100, app.height/6 + 90, 12*app.width/100, app.height/6 + 120, fill="white")
    canvas.create_text(19*app.width/200, app.height/6 + 125, anchor="n", text="(2-25)")
    canvas.create_text(7*app.width/100 + 7, app.height/6 + 120, anchor="sw", font="Helvetica 15", text=app.barSettings[0])
    canvas.create_text(15*app.width/100, app.height/6+120, text="Type:", anchor="sw", font="Helvetica 18")
    if(app.barSettings[1] == "songs"):
        canvas.create_rectangle(28*app.width/100, app.height/6 + 90, 34*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(35*app.width/100, app.height/6 + 90, 41*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.barSettings[1] == "artists"):
        canvas.create_rectangle(21*app.width/100, app.height/6 + 90, 27*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(35*app.width/100, app.height/6 + 90, 41*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.barSettings[1] == "albums"):
        canvas.create_rectangle(21*app.width/100, app.height/6 + 90, 27*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(28*app.width/100, app.height/6 + 90, 34*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    canvas.create_text(24*app.width/100, app.height/6+107, text="Songs", font="Helvetica 15", anchor="center")
    canvas.create_text(31*app.width/100, app.height/6+107, text="Artists", font="Helvetica 15", anchor="center")
    canvas.create_text(38*app.width/100, app.height/6+107, text="Albums", font="Helvetica 15", anchor="center")


    if(app.barSettings[2] == "7day"):
        canvas.create_rectangle(58.5*app.width/100, app.height/6 + 90, 66*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(67*app.width/100, app.height/6 + 90, 75*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(76*app.width/100, app.height/6 + 90, 84*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(85*app.width/100, app.height/6 + 90, 91*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(92*app.width/100, app.height/6 + 90, 98*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.barSettings[2] == "1month"):
        canvas.create_rectangle(50.5*app.width/100, app.height/6 + 90, 57.5*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(67*app.width/100, app.height/6 + 90, 75*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(76*app.width/100, app.height/6 + 90, 84*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(85*app.width/100, app.height/6 + 90, 91*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(92*app.width/100, app.height/6 + 90, 98*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.barSettings[2] == "3month"):
        canvas.create_rectangle(50.5*app.width/100, app.height/6 + 90, 57.5*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(58.5*app.width/100, app.height/6 + 90, 66*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(76*app.width/100, app.height/6 + 90, 84*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(85*app.width/100, app.height/6 + 90, 91*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(92*app.width/100, app.height/6 + 90, 98*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.barSettings[2] == "6month"):
        canvas.create_rectangle(50.5*app.width/100, app.height/6 + 90, 57.5*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(58.5*app.width/100, app.height/6 + 90, 66*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(67*app.width/100, app.height/6 + 90, 75*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(85*app.width/100, app.height/6 + 90, 91*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(92*app.width/100, app.height/6 + 90, 98*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.barSettings[2] == "12month"):
        canvas.create_rectangle(50.5*app.width/100, app.height/6 + 90, 57.5*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(58.5*app.width/100, app.height/6 + 90, 66*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(67*app.width/100, app.height/6 + 90, 75*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(76*app.width/100, app.height/6 + 90, 84*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(92*app.width/100, app.height/6 + 90, 98*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.barSettings[2] == "overall"):
        canvas.create_rectangle(50.5*app.width/100, app.height/6 + 90, 57.5*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(58.5*app.width/100, app.height/6 + 90, 66*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(67*app.width/100, app.height/6 + 90, 75*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(76*app.width/100, app.height/6 + 90, 84*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(85*app.width/100, app.height/6 + 90, 91*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    canvas.create_text(44*app.width/100, app.height/6 + 120, text="Time:", anchor="sw", font="Helvetica 18")
    canvas.create_text(54*app.width/100, app.height/6 + 107, text="1 Week", font="Helvetica 15", anchor="center")
    canvas.create_text(62*app.width/100, app.height/6 + 107, text="1 Month", font="Helvetica 15")
    canvas.create_text(71*app.width/100, app.height/6 + 107, text="3 Months", font="Helvetica 15")
    canvas.create_text(80*app.width/100, app.height/6 + 107, text="6 Months", font="Helvetica 15")
    canvas.create_text(88*app.width/100, app.height/6 + 107, text="1 Year", font="Helvetica 15")
    canvas.create_text(95*app.width/100, app.height/6 + 107, text="Overall", font="Helvetica 15")
    if(app.drawBar):
        drawBarGraph(app, canvas)

def barGraphMode_mousePressed(app, event):
    x, y = event.x, event.y
    if(y >= 0 and y <= app.height/6):
        if(x >= 2 * app.width/4 and x <= 3 * app.width/4):
            app.mode = "queryMode"
        elif(x >= 0 and x <= app.width/4):
            app.mode = "searchMode"
        elif(x >= app.width/4):
            app.mode = "exportMode"
    if(mouseInBox(x, y, 67*app.width/100,app.height/6+20, 83*app.width/100, app.height/6+80)):
        app.mode="lineGraphMode"
    if(mouseInBox(x, y, 17*app.width/100,app.height/6+20, 33*app.width/100, app.height/6+80)):
        app.mode="pieChartMode"
    if(mouseInBox(x, y, 7*app.width/100, app.height/6 + 90, 12*app.width/100, app.height/6 + 120)):
        app.selectedBar = True
    else:
        app.selectedBar = False
    if(mouseInBox(x, y,28*app.width/100, app.height/6 + 90, 34*app.width/100, app.height/6 + 125)):
        app.barSettings = (app.barSettings[0], "artists", app.barSettings[2])
    elif(mouseInBox(x, y,35*app.width/100, app.height/6 + 90, 41*app.width/100, app.height/6 + 125)):
        app.barSettings = (app.barSettings[0], "albums", app.barSettings[2])
    elif(mouseInBox(x, y,21*app.width/100, app.height/6 + 90, 27*app.width/100, app.height/6 + 125)):
        app.barSettings = (app.barSettings[0], "songs", app.barSettings[2])
    if(mouseInBox(x, y,50.5*app.width/100, app.height/6 + 90, 57.5*app.width/100, app.height/6 + 125)):
        app.barSettings = (app.barSettings[0], app.barSettings[1], "7day")
    if(mouseInBox(x, y,58.5*app.width/100, app.height/6 + 90, 66*app.width/100, app.height/6 + 125,)):
        app.barSettings = (app.barSettings[0], app.barSettings[1], "1month")
    if(mouseInBox(x, y,67*app.width/100, app.height/6 + 90, 75*app.width/100, app.height/6 + 125)):
        app.barSettings = (app.barSettings[0], app.barSettings[1], "3month")
    if(mouseInBox(x, y,76*app.width/100, app.height/6 + 90, 84*app.width/100, app.height/6 + 125)):
        app.barSettings = (app.barSettings[0], app.barSettings[1], "6month")
    if(mouseInBox(x, y,85*app.width/100, app.height/6 + 90, 91*app.width/100, app.height/6 + 125)):
        app.barSettings = (app.barSettings[0], app.barSettings[1], "12month")
    if(mouseInBox(x, y,92*app.width/100, app.height/6 + 90, 98*app.width/100, app.height/6 + 125)):
        app.barSettings = (app.barSettings[0], app.barSettings[1], "overall")

def barGraphMode_keyPressed(app, event):
    key = event.key
    if(len(app.barSettings[0]) == 0 and key == "0"):
        return
    if(app.selectedBar):
        if(key.isnumeric() or key == "backspace" or key == "Backspace"):
            if(key.isnumeric() and int(app.barSettings[0] + key) < 26):
                app.barSettings = (app.barSettings[0]+key, app.barSettings[1], app.barSettings[2])
            elif(key == "backspace" or key == "Backspace"):
                app.barSettings = (app.barSettings[0][:-1], app.barSettings[1], app.barSettings[2])
    if((key == "enter" or key == "Enter") and app.barSettings[0] != "" and int(app.barSettings[0]) > 1):
        getBarData(app)

def getBarData(app):
    app.max = 0
    app.encodedBarData = {}
    num, tipe,  times = app.barSettings
    if(tipe == "songs"):
        getSongUrl = f"?method=user.gettoptracks&user={app.LASTFM_USER}&period={ times}&api_key={app.LASTFM_KEY}&limit={num}&format=json"
        getSongRequest = requests.get(app.LASTFM_URL+getSongUrl)
        request = getSongRequest.json()
        print(json.dumps(request, indent=1))
        app.barData = request["toptracks"]["track"]
    elif(tipe == "artists"):
        getArtistUrl = f"?method=user.gettopartists&user={app.LASTFM_USER}&period={ times}&api_key={app.LASTFM_KEY}&limit={num}&format=json"
        getArtistRequest = requests.get(app.LASTFM_URL+getArtistUrl)
        request = getArtistRequest.json()
        print(json.dumps(request, indent=1))
        app.barData = request["topartists"]["artist"]
    elif(tipe == "albums"):
        getAlbumUrl = f"?method=user.gettopalbums&user={app.LASTFM_USER}&period={times}&api_key={app.LASTFM_KEY}&limit={num}&format=json"
        getAlbumRequest = requests.get(app.LASTFM_URL+getAlbumUrl)
        request = getAlbumRequest.json()
        print(json.dumps(request, indent=1))
        app.barData = request["topalbums"]["album"]
    
    for i in app.barData:
        if(int(i.get("playcount")) > app.max):
            app.max = int(i.get("playcount"))
    print(app.max)
    for i in app.barData:
        app.encodedBarData[i.get("name")] = (int(i.get("playcount"))/app.max)
    print(app.encodedBarData)
    app.drawBar = True

def drawBarGraph(app, canvas):
    count = 0
    margin = 10
    bottomLine = app.height/3 + 20 + 2*app.height/3-30
    maxHeight = (bottomLine) - (app.height/3+20)
    barWidth = (app.width/2-6*margin-(margin*len(app.encodedBarData)))/len(app.encodedBarData)
    canvas.create_text(30, app.height/3+20, text=app.max, anchor="e", font="Helvetica 13")
    canvas.create_line(40, app.height/3+20, 40, bottomLine)
    canvas.create_line(40, bottomLine, app.width/2, bottomLine)
    for key in app.encodedBarData:
        canvas.create_rectangle(40 +margin + margin*count + barWidth*count, bottomLine - app.encodedBarData.get(key)*(maxHeight), 
                                40 + margin + margin*count + barWidth*count + barWidth, bottomLine,
                                fill=app.colors[count])
        canvas.create_rectangle(app.width/2 + (count//13)*app.width/4, app.height/3 + 20 + (count%13)*app.width/36, 
                                app.width/2 + (count//13)*app.width/4 + 20, app.height/3 + 20 + (count%13)*app.width/36 + 20,
                                fill=app.colors[count], outline=app.colors[count])
        canvas.create_text(app.width/2 + (count//13)*app.width/4 + 35, app.height/3 + 20 + (count%13)*app.width/36 + 20,
                            anchor="sw", text=key)
        count += 1
    canvas.create_text(30, bottomLine-(1*maxHeight/8), text=app.max//8, anchor="e", font="Helvetica 13")
    canvas.create_text(30, bottomLine-(2*maxHeight/8), text=2*app.max//8, anchor="e", font="Helvetica 13")
    canvas.create_text(30, bottomLine-(3*maxHeight/8), text=3*app.max//8, anchor="e", font="Helvetica 13")
    canvas.create_text(30, bottomLine-(4*maxHeight/8), text=4*app.max//8, anchor="e", font="Helvetica 13")
    canvas.create_text(30, bottomLine-(5*maxHeight/8), text=5*app.max//8, anchor="e", font="Helvetica 13")
    canvas.create_text(30, bottomLine-(6*maxHeight/8), text=6*app.max//8, anchor="e", font="Helvetica 13")
    canvas.create_text(30, bottomLine-(7*maxHeight/8), text=7*app.max//8, anchor="e", font="Helvetica 13")
    canvas.create_text(30, bottomLine-(8*maxHeight/8), text=8*app.max//8, anchor="e", font="Helvetica 13")
    canvas.create_line(35, bottomLine-(2*maxHeight/8), 45, bottomLine-(2*maxHeight/8))
    canvas.create_line(35, bottomLine-(3*maxHeight/8), 45, bottomLine-(3*maxHeight/8))
    canvas.create_line(35, bottomLine-(4*maxHeight/8), 45, bottomLine-(4*maxHeight/8))
    canvas.create_line(35, bottomLine-(5*maxHeight/8), 45, bottomLine-(5*maxHeight/8))
    canvas.create_line(35, bottomLine-(6*maxHeight/8), 45, bottomLine-(6*maxHeight/8))
    canvas.create_line(35, bottomLine-(1*maxHeight/8), 45, bottomLine-(1*maxHeight/8))
    canvas.create_line(35, bottomLine-(7*maxHeight/8), 45, bottomLine-(7*maxHeight/8))
    canvas.create_line(35, bottomLine-(8*maxHeight/8), 45, bottomLine-(8*maxHeight/8))

##########################################
# Line Graph Mode
##########################################

def lineGraphMode_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill="#FFA8B7", 
                            outline="#FFA8B7")
    canvas.create_rectangle(0, app.height/6, app.width, app.height, fill="#FFC0CB",
                            outline="#FFC0CB")
    canvas.create_rectangle(app.width/4, 0, app.width/2, app.height/6, fill="#FFC0CB",
                            outline="#FFC0CB")
    # canvas.create_line(app.width/4, 0, app.width/2, app.height/6, fill="#FFC0CB")
    canvas.create_line(3*app.width/4, 0, 3*app.width/4, app.height/6, fill="#FFC0CB")
    canvas.create_text(app.width/8, app.height/12, text="Search", font="Helvetica 35")
    canvas.create_text(3*app.width/8, app.height/12, text="Graphs", font="Helvetica 35")
    canvas.create_text(5*app.width/8, app.height/12, text="Queries", font="Helvetica 35")
    canvas.create_text(7*app.width/8, app.height/12, text="Export", font="Helvetica 35")
    canvas.create_rectangle(42*app.width/100,app.height/6+20, 58*app.width/100, app.height/6+80, fill="#FFA8B7", outline="#FFA8B7")
    canvas.create_rectangle(17*app.width/100,app.height/6+20, 33*app.width/100, app.height/6+80, fill="#FFA8B7", outline="#FFA8B7")
    canvas.create_text(app.width/4, app.height/6 + 50, text="Pie Chart", font="Helvetica 20")
    canvas.create_text(2*app.width/4, app.height/6 + 50, text="Bar Graph", font="Helvetica 20")
    canvas.create_text(3*app.width/4, app.height/6 + 50, text="Line Graph", font="Helvetica 20")
    canvas.create_text(6*app.width/100, app.height/6 + 120, text="Top:", anchor="se",font="Helvetica 18")
    canvas.create_rectangle(7*app.width/100, app.height/6 + 90, 12*app.width/100, app.height/6 + 120, fill="white")
    canvas.create_text(19*app.width/200, app.height/6 + 125, anchor="n", text="(2-25)")
    canvas.create_text(7*app.width/100 + 7, app.height/6 + 120, anchor="sw", font="Helvetica 15", text=app.lineSettings[0])
    canvas.create_text(15*app.width/100, app.height/6+120, text="Type:", anchor="sw", font="Helvetica 18")
    if(app.lineSettings[1] == "songs"):
        canvas.create_rectangle(28*app.width/100, app.height/6 + 90, 34*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(35*app.width/100, app.height/6 + 90, 41*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.lineSettings[1] == "artists"):
        canvas.create_rectangle(21*app.width/100, app.height/6 + 90, 27*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(35*app.width/100, app.height/6 + 90, 41*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.lineSettings[1] == "albums"):
        canvas.create_rectangle(21*app.width/100, app.height/6 + 90, 27*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(28*app.width/100, app.height/6 + 90, 34*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    canvas.create_text(24*app.width/100, app.height/6+107, text="Songs", font="Helvetica 15", anchor="center")
    canvas.create_text(31*app.width/100, app.height/6+107, text="Artists", font="Helvetica 15", anchor="center")
    canvas.create_text(38*app.width/100, app.height/6+107, text="Albums", font="Helvetica 15", anchor="center")


    if(app.lineSettings[2] == "7day"):
        canvas.create_rectangle(58.5*app.width/100, app.height/6 + 90, 66*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(67*app.width/100, app.height/6 + 90, 75*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(76*app.width/100, app.height/6 + 90, 84*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(85*app.width/100, app.height/6 + 90, 91*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.lineSettings[2] == "1month"):
        canvas.create_rectangle(50.5*app.width/100, app.height/6 + 90, 57.5*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(67*app.width/100, app.height/6 + 90, 75*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(76*app.width/100, app.height/6 + 90, 84*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(85*app.width/100, app.height/6 + 90, 91*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.lineSettings[2] == "3month"):
        canvas.create_rectangle(50.5*app.width/100, app.height/6 + 90, 57.5*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(58.5*app.width/100, app.height/6 + 90, 66*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(76*app.width/100, app.height/6 + 90, 84*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(85*app.width/100, app.height/6 + 90, 91*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.lineSettings[2] == "6month"):
        canvas.create_rectangle(50.5*app.width/100, app.height/6 + 90, 57.5*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(58.5*app.width/100, app.height/6 + 90, 66*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(67*app.width/100, app.height/6 + 90, 75*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(85*app.width/100, app.height/6 + 90, 91*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    elif(app.lineSettings[2] == "12month"):
        canvas.create_rectangle(50.5*app.width/100, app.height/6 + 90, 57.5*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(58.5*app.width/100, app.height/6 + 90, 66*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(67*app.width/100, app.height/6 + 90, 75*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
        canvas.create_rectangle(76*app.width/100, app.height/6 + 90, 84*app.width/100, app.height/6 + 125, fill="#FFA8B7", outline="#FFA8B7")
    canvas.create_text(44*app.width/100, app.height/6 + 120, text="Time:", anchor="sw", font="Helvetica 18")
    canvas.create_text(54*app.width/100, app.height/6 + 107, text="1 Week", font="Helvetica 15", anchor="center")
    canvas.create_text(62*app.width/100, app.height/6 + 107, text="1 Month", font="Helvetica 15")
    canvas.create_text(71*app.width/100, app.height/6 + 107, text="3 Months", font="Helvetica 15")
    canvas.create_text(80*app.width/100, app.height/6 + 107, text="6 Months", font="Helvetica 15")
    canvas.create_text(88*app.width/100, app.height/6 + 107, text="1 Year", font="Helvetica 15")
    if(app.drawLine):
        drawLineGraph(app, canvas)

def lineGraphMode_mousePressed(app, event):
    x, y = event.x, event.y
    if(y >= 0 and y <= app.height/6):
        if(x >= 2 * app.width/4 and x <= 3 * app.width/4):
            app.mode = "queryMode"
        elif(x >= 0 and x <= app.width/4):
            app.mode = "searchMode"
        elif(x >= app.width/4):
            app.mode = "exportMode"
    if(mouseInBox(x, y, 42*app.width/100,app.height/6+20, 58*app.width/100, app.height/6+80)):
        app.mode="barGraphMode"
    if(mouseInBox(x, y, 17*app.width/100,app.height/6+20, 33*app.width/100, app.height/6+80)):
        app.mode="pieChartMode"
    if(mouseInBox(x, y, 7*app.width/100, app.height/6 + 90, 12*app.width/100, app.height/6 + 120)):
        app.selectedLine = True
    else:
        app.selectedLine = False
    if(mouseInBox(x, y,28*app.width/100, app.height/6 + 90, 34*app.width/100, app.height/6 + 125)):
        app.lineSettings = (app.lineSettings[0], "artists", app.lineSettings[2])
    elif(mouseInBox(x, y,35*app.width/100, app.height/6 + 90, 41*app.width/100, app.height/6 + 125)):
        app.lineSettings = (app.lineSettings[0], "albums", app.lineSettings[2])
    elif(mouseInBox(x, y,21*app.width/100, app.height/6 + 90, 27*app.width/100, app.height/6 + 125)):
        app.lineSettings = (app.lineSettings[0], "songs", app.lineSettings[2])
    if(mouseInBox(x, y,50.5*app.width/100, app.height/6 + 90, 57.5*app.width/100, app.height/6 + 125)):
        app.lineSettings = (app.lineSettings[0], app.lineSettings[1], "7day")
    if(mouseInBox(x, y,58.5*app.width/100, app.height/6 + 90, 66*app.width/100, app.height/6 + 125,)):
        app.lineSettings = (app.lineSettings[0], app.lineSettings[1], "1month")
    if(mouseInBox(x, y,67*app.width/100, app.height/6 + 90, 75*app.width/100, app.height/6 + 125)):
        app.lineSettings = (app.lineSettings[0], app.lineSettings[1], "3month")
    if(mouseInBox(x, y,76*app.width/100, app.height/6 + 90, 84*app.width/100, app.height/6 + 125)):
        app.lineSettings = (app.lineSettings[0], app.lineSettings[1], "6month")
    if(mouseInBox(x, y,85*app.width/100, app.height/6 + 90, 91*app.width/100, app.height/6 + 125)):
        app.lineSettings = (app.lineSettings[0], app.lineSettings[1], "12month")

def lineGraphMode_keyPressed(app, event):
    key = event.key
    if(len(app.lineSettings[0]) == 0 and key == "0"):
        return
    if(app.selectedLine):
        if(key.isnumeric() or key == "backspace" or key == "Backspace"):
            if(key.isnumeric() and int(app.lineSettings[0] + key) < 26):
                app.lineSettings = (app.lineSettings[0]+key, app.lineSettings[1], app.lineSettings[2])
            elif(key == "backspace" or key == "Backspace"):
                app.lineSettings = (app.lineSettings[0][:-1], app.lineSettings[1], app.lineSettings[2])
    if((key == "enter" or key == "Enter") and app.lineSettings[0] != "" and int(app.lineSettings[0]) > 0):
        getLineData(app)

def getLineData(app):
    app.max = 0
    app.encodedLineData = {}
    num, tipe, times = app.lineSettings
    if(tipe == "songs"):
        getSongUrl = f"?method=user.gettoptracks&user={app.LASTFM_USER}&period={times}&api_key={app.LASTFM_KEY}&limit={num}&format=json"
        getSongRequest = requests.get(app.LASTFM_URL+getSongUrl)
        request = getSongRequest.json()
        print(json.dumps(request, indent=1))
        app.lineData = request["toptracks"]["track"]
    elif(tipe == "artists"):
        getArtistUrl = f"?method=user.gettopartists&user={app.LASTFM_USER}&period={times}&api_key={app.LASTFM_KEY}&limit={num}&format=json"
        getArtistRequest = requests.get(app.LASTFM_URL+getArtistUrl)
        request = getArtistRequest.json()
        print(json.dumps(request, indent=1))
        app.lineData = request["topartists"]["artist"]
    elif(tipe == "albums"):
        getAlbumUrl = f"?method=user.gettopalbums&user={app.LASTFM_USER}&period={times}&api_key={app.LASTFM_KEY}&limit={num}&format=json"
        getAlbumRequest = requests.get(app.LASTFM_URL+getAlbumUrl)
        request = getAlbumRequest.json()
        print(json.dumps(request, indent=1))
        app.lineData = request["topalbums"]["album"]
    print("linedata", app.lineData)
    time0 = time.time()
    if(times == "7day"):
        app.linePoints = 7
        for i in app.lineData:
            app.encodedLineData[i.get("name")] = [0]*7
        with open(f"{app.LASTFM_USER}_songs.json", "r") as fp:
            allSongs = json.load(fp)
        for i in allSongs:
            if(i.get("date") == None): continue
            if(int(i.get("date").get("uts")) < (time0 - 7*86400)):
                break
            for count in range(7):
                if(int(i.get("date").get("uts")) > time0-(count+1)*(86400) and int(i.get("date").get("uts")) < time0-(86400)*(count)):
                    if(tipe == "songs"):
                        if(i.get("name") in app.encodedLineData):
                            app.encodedLineData.get(i.get("name"))[count] += 1
                            continue
                    elif(tipe == "artists"):
                        if(i.get("artist").get("#text") in app.encodedLineData):
                            app.encodedLineData.get(i.get("artist").get("#text"))[count] += 1
                            continue
                    elif(tipe == "albums"):
                        if(i.get("album").get("#text") in app.encodedLineData):
                            app.encodedLineData.get(i.get("album").get("#text"))[count] += 1
                            continue
    if(times == "1month"):
        app.linePoints = 15
        for i in app.lineData:
            app.encodedLineData[i.get("name")] = [0]*15
        with open(f"{app.LASTFM_USER}_songs.json", "r") as fp:
            allSongs = json.load(fp)
        for i in allSongs:
            if(i.get("date") == None): continue
            if(int(i.get("date").get("uts")) < (time0 - 30*86400)):
                break
            for count in range(15):
                if(int(i.get("date").get("uts")) > time0-(count+1)*(172800) and int(i.get("date").get("uts")) < time0-(172800)*(count)):
                    if(tipe == "songs"):
                        if(i.get("name") in app.encodedLineData):
                            app.encodedLineData.get(i.get("name"))[count] += 1
                            continue
                    elif(tipe == "artists"):
                        if(i.get("artist").get("#text") in app.encodedLineData):
                            app.encodedLineData.get(i.get("artist").get("#text"))[count] += 1
                            continue
                    elif(tipe == "albums"):
                        if(i.get("album").get("#text") in app.encodedLineData):
                            app.encodedLineData.get(i.get("album").get("#text"))[count] += 1
                            continue
    elif(times == "3month"):
        app.linePoints = 15
        for i in app.lineData:
            app.encodedLineData[i.get("name")] = [0]*15
        with open(f"{app.LASTFM_USER}_songs.json", "r") as fp:
            allSongs = json.load(fp)
        for i in allSongs:
            if(i.get("date") == None): continue
            if(int(i.get("date").get("uts")) < (time0 - 90*86400)):
                break
            for count in range(15):
                if(int(i.get("date").get("uts")) > time0-(count+1)*(518400) and int(i.get("date").get("uts")) < time0-(518400)*(count)):
                    if(tipe == "songs"):
                        if(i.get("name") in app.encodedLineData):
                            app.encodedLineData.get(i.get("name"))[count] += 1
                            continue
                    elif(tipe == "artists"):
                        if(i.get("artist").get("#text") in app.encodedLineData):
                            app.encodedLineData.get(i.get("artist").get("#text"))[count] += 1
                            continue
                    elif(tipe == "albums"):
                        if(i.get("album").get("#text") in app.encodedLineData):
                            app.encodedLineData.get(i.get("album").get("#text"))[count] += 1
                            continue
    elif(times == "6month"):
        app.linePoints = 12
        for i in app.lineData:
            app.encodedLineData[i.get("name")] = [0]*12
        with open(f"{app.LASTFM_USER}_songs.json", "r") as fp:
            allSongs = json.load(fp)
        for i in allSongs:
            if(i.get("date") == None): continue
            if(int(i.get("date").get("uts")) < (time0 - 180*86400)):
                break
            for count in range(12):
                if(int(i.get("date").get("uts")) > time0-(count+1)*(1296000) and int(i.get("date").get("uts")) < time0-(1296000)*(count)):
                    if(tipe == "songs"):
                        if(i.get("name") in app.encodedLineData):
                            app.encodedLineData.get(i.get("name"))[count] += 1
                            continue
                    elif(tipe == "artists"):
                        if(i.get("artist").get("#text") in app.encodedLineData):
                            app.encodedLineData.get(i.get("artist").get("#text"))[count] += 1
                            continue
                    elif(tipe == "albums"):
                        if(i.get("album").get("#text") in app.encodedLineData):
                            app.encodedLineData.get(i.get("album").get("#text"))[count] += 1
                            continue
    elif(times == "12month"):
        app.linePoints = 12
        for i in app.lineData:
            app.encodedLineData[i.get("name")] = [0]*12
        with open(f"{app.LASTFM_USER}_songs.json", "r") as fp:
            allSongs = json.load(fp)
        for i in allSongs:
            if(i.get("date") == None): continue
            if(int(i.get("date").get("uts")) < (time0 - 365*86400)):
                break
            for count in range(12):
                if(int(i.get("date").get("uts")) > time0-(count+1)*(2628000) and int(i.get("date").get("uts")) < time0-(2628000)*(count)):
                    if(tipe == "songs"):
                        if(i.get("name") in app.encodedLineData):
                            app.encodedLineData.get(i.get("name"))[count] += 1
                            continue
                    elif(tipe == "artists"):
                        if(i.get("artist").get("#text") in app.encodedLineData):
                            app.encodedLineData.get(i.get("artist").get("#text"))[count] += 1
                            continue
                    elif(tipe == "albums"):
                        if(i.get("album").get("#text") in app.encodedLineData):
                            app.encodedLineData.get(i.get("album").get("#text"))[count] += 1
                            continue
    app.lineMax = 0
    for i in app.encodedLineData:
        for p in app.encodedLineData.get(i):
            if int(p) > app.lineMax:
                app.lineMax = int(p)
    for i in app.encodedLineData:
        for p in range(len(app.encodedLineData[i])):
            app.encodedLineData[i][p] = float(app.encodedLineData[i][p])/app.lineMax
    print(app.encodedLineData)
    app.drawLine = True

def drawLineGraph(app, canvas):
    count = 0
    bottomLine = app.height/3 + 20 + 2*app.height/3-50
    maxHeight = (bottomLine) - (app.height/3+20)
    pointWidth = ((app.width/2)-20)/app.linePoints
    canvas.create_text(30, bottomLine-(1*maxHeight/8), text=app.lineMax//8, anchor="e", font="Helvetica 13")
    canvas.create_text(30, bottomLine-(2*maxHeight/8), text=2*app.lineMax//8, anchor="e", font="Helvetica 13")
    canvas.create_text(30, bottomLine-(3*maxHeight/8), text=3*app.lineMax//8, anchor="e", font="Helvetica 13")
    canvas.create_text(30, bottomLine-(4*maxHeight/8), text=4*app.lineMax//8, anchor="e", font="Helvetica 13")
    canvas.create_text(30, bottomLine-(5*maxHeight/8), text=5*app.lineMax//8, anchor="e", font="Helvetica 13")
    canvas.create_text(30, bottomLine-(6*maxHeight/8), text=6*app.lineMax//8, anchor="e", font="Helvetica 13")
    canvas.create_text(30, bottomLine-(7*maxHeight/8), text=7*app.lineMax//8, anchor="e", font="Helvetica 13")
    canvas.create_text(30, bottomLine-(8*maxHeight/8), text=8*app.lineMax//8, anchor="e", font="Helvetica 13")
    canvas.create_line(35, bottomLine-(2*maxHeight/8), 45, bottomLine-(2*maxHeight/8))
    canvas.create_line(35, bottomLine-(3*maxHeight/8), 45, bottomLine-(3*maxHeight/8))
    canvas.create_line(35, bottomLine-(4*maxHeight/8), 45, bottomLine-(4*maxHeight/8))
    canvas.create_line(35, bottomLine-(5*maxHeight/8), 45, bottomLine-(5*maxHeight/8))
    canvas.create_line(35, bottomLine-(6*maxHeight/8), 45, bottomLine-(6*maxHeight/8))
    canvas.create_line(35, bottomLine-(1*maxHeight/8), 45, bottomLine-(1*maxHeight/8))
    canvas.create_line(35, bottomLine-(7*maxHeight/8), 45, bottomLine-(7*maxHeight/8))
    canvas.create_line(35, bottomLine-(8*maxHeight/8), 45, bottomLine-(8*maxHeight/8))

    temp = 0
    for key in app.encodedLineData:
        temp = len(app.encodedLineData.get(key))
        for i in range(len(app.encodedLineData[key])-1):
            canvas.create_line(40+i*pointWidth, bottomLine - maxHeight*app.encodedLineData.get(key)[i], 
            40+(i+1)*pointWidth, bottomLine - maxHeight*app.encodedLineData.get(key)[i+1],
            fill=app.colors[count], width=2)
            canvas.create_rectangle(app.width/2 + (count//13)*app.width/4, app.height/3 + 20 + (count%13)*app.width/36, 
                                app.width/2 + (count//13)*app.width/4 + 20, app.height/3 + 20 + (count%13)*app.width/36 + 20,
                                fill=app.colors[count], outline=app.colors[count])
        canvas.create_text(app.width/2 + (count//13)*app.width/4 + 35, app.height/3 + 20 + (count%13)*app.width/36 + 20,
                            anchor="sw", text=key)
        count += 1
    canvas.create_line(40, app.height/3+20, 40, bottomLine)
    canvas.create_line(40, bottomLine, 40+(temp-1)*pointWidth, bottomLine)

##########################################
# Query Mode
##########################################

def queryMode_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill="#FFA8B7", 
                            outline="#FFA8B7")
    canvas.create_rectangle(0, app.height/6, app.width, app.height, fill="#FFC0CB",
                            outline="#FFC0CB")
    canvas.create_rectangle(app.width/2, 0, 3*app.width/4, app.height/6, fill="#FFC0CB",
                            outline="#FFC0CB")
    canvas.create_line(app.width/4, 0, app.width/4, app.height/6, fill="#FFC0CB")
  #  canvas.create_line(3*app.width/4, 0, 3*app.width/4, app.height/6, fill="#FFC0CB")
    canvas.create_text(app.width/8, app.height/12, text="Search", font="Helvetica 35")
    canvas.create_text(3*app.width/8, app.height/12, text="Graphs", font="Helvetica 35")
    canvas.create_text(5*app.width/8, app.height/12, text="Queries", font="Helvetica 35")
    canvas.create_text(7*app.width/8, app.height/12, text="Export", font="Helvetica 35")
    for i in range(app.queryPage*5, app.queryPage*5+5):
        if(i < len(app.queryList)):
            fill="black"
            if(app.queryList[i] in app.selectedSongs):
                fill="blue"
            canvas.create_text(10, (22+(i%5)*4)*app.height/40, text=app.queryList[i].get("name"), anchor="w", fill=fill, font="Helvetica 12")
            canvas.create_text(2.75*app.width/5, (22+(i%5)*4)*app.height/40, text=app.queryList[i].get("album"), anchor="w", font="Helvetica 12")
            canvas.create_text(1.5*app.width/5, (22+(i%5)*4)*app.height/40, text=app.queryList[i].get("artist").get("name"), anchor="w", font="Helvetica 12")
            canvas.create_text(4.25*app.width/5, (22+(i%5)*4)*app.height/40, text=app.queryList[i].get("playcount"), anchor="w", font="Helvetica 12")
            tot = int(app.queryList[i].get("duration"))
            secs = tot%60
            mins = tot//60
            if(secs < 10):
                secs = f"0{secs}"
            canvas.create_text(4.5*app.width/5, (22+(i%5)*4)*app.height/40, text=f"{mins}:{secs}", anchor="w", font="Helvetica 12")
    canvas.create_polygon(app.width-40, app.height-30, app.width-20, app.height-30, app.width-30, app.height-17.321)
    canvas.create_polygon(app.width-40, 22*app.height/40+12.7, app.width-20, 22*app.height/40+12.7, app.width-30, 22*app.height/40)
    canvas.create_line(0,20*app.height/40, app.width, 20*app.height/40)
    canvas.create_line(0,24*app.height/40, app.width, 24*app.height/40)
    canvas.create_line(0,28*app.height/40, app.width, 28*app.height/40)
    canvas.create_line(0,32*app.height/40, app.width, 32*app.height/40)
    canvas.create_line(0,36*app.height/40, app.width, 36*app.height/40)
    canvas.create_text(10, 20*app.height/40, anchor="sw", text="Title:", font="Helvetica 18")
    canvas.create_text(2.75*app.width/5, 20*app.height/40, anchor="sw", text="Album", font="Helvetica 18")
    canvas.create_text(1.5*app.width/5, 20*app.height/40, anchor="sw", text="Artist", font="Helvetica 18")
    canvas.create_text(4.25*app.width/5, 20*app.height/40, anchor="se", text="Plays", font="Helvetica 18")
    canvas.create_text(4.5*app.width/5, 20*app.height/40, anchor="sw", text="Length", font="Helvetica 18")
    canvas.create_text(app.width/2-200, 4*app.height/12, anchor="center",text="What are the 50 songs I am most likely to listen to at: ", font="Helvetica 18")
    canvas.create_rectangle(app.width/2+90, 7.5*app.height/24, app.width/2+175, 8.5*app.height/24, outline="black", fill="white")
    canvas.create_text(app.width/2+95, 8.5*app.height/24-2, anchor="sw", text=app.timeQuery, font="Helvetica 14")
    canvas.create_text(app.width/2+132.5, 8.5*app.height/24, anchor="n", text="Format: hh:mm")
    canvas.create_text(app.width/2+132.5, 7.5*app.height/24, anchor="s", text="24hr Time")
    canvas.create_text(app.width/2+180, 8.5*app.height/24, anchor="sw", text="?", font="Helvetica 18")


def queryMode_mousePressed(app, event):
    x, y = event.x, event.y
    if(y >= 0 and y <= app.height/6):
        if(x >= app.width/4 and x <= 2* app.width/4):
            app.mode = "pieChartMode"
        elif(x >= 0 and x <= app.width/4):
            app.mode = "searchMode"
        elif(x >= app.width/4):
            app.mode = "exportMode"
    if(mouseInBox(x, y, app.width-40, app.height-30, app.width-20, app.height-17.321)):
        if(app.queryPage < math.ceil(len(app.queryList)/5)-1):
            app.queryPage += 1
    elif(mouseInBox(x, y, app.width-40, 22*app.height/40, app.width-20, 22*app.height/40+12.7)):
        if(app.queryPage > 0):
            app.queryPage -= 1
    if(mouseInBox(x, y, app.width/2+90, 7.5*app.height/24, app.width/2+175, 8.5*app.height/24)):
        app.querySelected = True
    else:
        app.querySelected = False
    try:
        if(mouseInBox(x, y, 0, 20*app.height/40, app.width - 45, 24*app.height/40)):
            if(app.queryList[app.queryPage*5] in app.selectedSongs):
                app.selectedSongs.remove(app.queryList[app.queryPage*5])
            else:
                app.selectedSongs.append(app.queryList[app.queryPage*5])
        elif(mouseInBox(x, y, 0, 24*app.height/40, app.width - 45, 28*app.height/40)):
            if(app.queryList[app.queryPage*5 + 1] in app.selectedSongs):
                app.selectedSongs.remove(app.queryList[app.queryPage*5 + 1])
            else:
                app.selectedSongs.append(app.queryList[app.queryPage*5 + 1])
        elif(mouseInBox(x, y, 0, 28*app.height/40, app.width - 45, 32*app.height/40)):
            if(app.queryList[app.queryPage*5 + 2] in app.selectedSongs):
                app.selectedSongs.remove(app.queryList[app.queryPage*5 + 2])
            else:
                app.selectedSongs.append(app.queryList[app.queryPage*5 + 2])
        elif(mouseInBox(x, y, 0, 32*app.height/40, app.width - 45, 36*app.height/40)):
            if(app.queryList[app.queryPage*5 + 3] in app.selectedSongs):
                app.selectedSongs.remove(app.queryList[app.queryPage*5 + 3])
            else:
                app.selectedSongs.append(app.queryList[app.queryPage*5 + 3])
        elif(mouseInBox(x, y, 0, 36*app.height/40, app.width - 45, 40*app.height/40)):
            if(app.queryList[app.queryPage*5 + 4] in app.selectedSongs):
                app.selectedSongs.remove(app.queryList[app.queryPage*5 + 4])
            else:
                app.selectedSongs.append(app.queryList[app.queryPage*5 + 4])
    except:
        pass

def findCloseToTime(app):
    if(":" not in app.timeQuery or len(app.timeQuery.split(":")) != 2 or len(app.timeQuery) > 5):
        return
    else:
        splitTime = app.timeQuery.split(":")
        if(splitTime[0].isnumeric() and splitTime[1].isnumeric()):
            hr, mins = int(splitTime[0]), int(splitTime[1])
            if(hr < 24 and hr >= 0 and mins >= 0 and mins < 60):
                app.totalMins = hr*60 + mins
            else:
                return
        else:
            return
    queryDict = {}
    with open(f"{app.LASTFM_USER}_songs.json", "r") as fp:
        allSongs = json.load(fp)
    for i in allSongs:
        if(i.get("date") == None):
            continue
        else:
            timeTuple = i.get("date").get("#text").split(",")[1][1:].split(":")
            curMins = int(timeTuple[0]) * 60 + int(timeTuple[1])
        #  or abs(app.totalMins-curMins) > 1434
        if(abs(app.totalMins-curMins) < 5):
            if(i.get("name") not in queryDict):
                queryDict[i.get("name")] = 1
            else:
                queryDict[i.get("name")] += 1
        #  or abs(app.totalMins-curMins) > 1429
        elif(abs(app.totalMins-curMins) < 10):
            if(i.get("name") not in queryDict):
                queryDict[i.get("name")] = .9
            else:
                queryDict[i.get("name")] += .9
        #  or abs(app.totalMins-curMins) > 1419
        elif(abs(app.totalMins-curMins) < 20):
            if(i.get("name") not in queryDict):
                queryDict[i.get("name")] = .6
            else:
                queryDict[i.get("name")] += .6
        #  or abs(app.totalMins-curMins) > 1399
        elif(abs(app.totalMins-curMins) < 40):
            if(i.get("name") not in queryDict):
                queryDict[i.get("name")] = .4
            else:
                queryDict[i.get("name")] += .4
        #  or abs(app.totalMins-curMins) > 1379
        elif(abs(app.totalMins-curMins) < 60):
            if(i.get("name") not in queryDict):
                queryDict[i.get("name")] = .15
            else:
                queryDict[i.get("name")] += .15
    count = 0
    # Dictionary sort based on value from https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    queryDict = dict(sorted(queryDict.items(), key=lambda item: item[1], reverse=True))
    allSongs = []
    topSongs = []
    with open(f"{app.LASTFM_USER}_topSongs.json", "r") as fp:
        topSongs = json.load(fp)
    app.queryList = []
    for i in queryDict:
        if(count >= 100):
            break
        for p in topSongs:
            if(p.get("name") == i):
                app.queryList.append(p)
                count+=1
    print(queryDict)
    
    

def queryMode_keyPressed(app, event):
    key = event.key
    if(key == "="):
        app.selectedSongs += app.queryList
    if(app.querySelected):
        if(len(key) == 1 or key == "backspace" or key == "Backspace"):
            if(len(key) == 1 and (key.isnumeric() or key == ":") and len(app.timeQuery) < 6):
                app.timeQuery += key
            elif(key == "backspace" or key == "Backspace"):
                app.timeQuery = app.timeQuery[:-1]
    if(key == "enter" or key == "Enter"):
        findCloseToTime(app)
    

##########################################
# Export Mode
##########################################

def exportMode_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill="#FFA8B7", 
                            outline="#FFA8B7")
    canvas.create_rectangle(0, app.height/6, app.width, app.height, fill="#FFC0CB",
                            outline="#FFC0CB")
    canvas.create_rectangle(3*app.width/4, 0, app.width, app.height/6, fill="#FFC0CB",
                            outline="#FFC0CB")
    canvas.create_line(app.width/4, 0, app.width/4, app.height/6, fill="#FFC0CB")
    canvas.create_line(app.width/2, 0, app.width/2, app.height/6, fill="#FFC0CB")
    canvas.create_text(app.width/8, app.height/12, text="Search", font="Helvetica 35")
    canvas.create_text(3*app.width/8, app.height/12, text="Graphs", font="Helvetica 35")
    canvas.create_text(5*app.width/8, app.height/12, text="Queries", font="Helvetica 35")
    canvas.create_text(7*app.width/8, app.height/12, text="Export", font="Helvetica 35")

    for i in range(app.exportPage*5, app.exportPage*5+5):
        if(i < len(app.selectedSongs)):
            fill="blue"
            canvas.create_text(10, (22+(i%5)*4)*app.height/40, text=app.selectedSongs[i].get("name"), anchor="w", fill=fill, font="Helvetica 12")
            canvas.create_text(2.75*app.width/5, (22+(i%5)*4)*app.height/40, text=app.selectedSongs[i].get("album"), anchor="w", font="Helvetica 12")
            canvas.create_text(1.5*app.width/5, (22+(i%5)*4)*app.height/40, text=app.selectedSongs[i].get("artist").get("name"), anchor="w", font="Helvetica 12")
            canvas.create_text(4.25*app.width/5, (22+(i%5)*4)*app.height/40, text=app.selectedSongs[i].get("playcount"), anchor="w", font="Helvetica 12")
            tot = int(app.selectedSongs[i].get("duration"))
            secs = tot%60
            mins = tot//60
            if(secs < 10):
                secs = f"0{secs}"
            canvas.create_text(4.5*app.width/5, (22+(i%5)*4)*app.height/40, text=f"{mins}:{secs}", anchor="w", font="Helvetica 12")
    canvas.create_polygon(app.width-40, app.height-30, app.width-20, app.height-30, app.width-30, app.height-17.321)
    canvas.create_polygon(app.width-40, 22*app.height/40+12.7, app.width-20, 22*app.height/40+12.7, app.width-30, 22*app.height/40)
    canvas.create_line(0,20*app.height/40, app.width, 20*app.height/40)
    canvas.create_line(0,24*app.height/40, app.width, 24*app.height/40)
    canvas.create_line(0,28*app.height/40, app.width, 28*app.height/40)
    canvas.create_line(0,32*app.height/40, app.width, 32*app.height/40)
    canvas.create_line(0,36*app.height/40, app.width, 36*app.height/40)
    canvas.create_text(10, 20*app.height/40, anchor="sw", text="Title:", font="Helvetica 18")
    canvas.create_text(2.75*app.width/5, 20*app.height/40, anchor="sw", text="Album", font="Helvetica 18")
    canvas.create_text(1.5*app.width/5, 20*app.height/40, anchor="sw", text="Artist", font="Helvetica 18")
    canvas.create_text(4.25*app.width/5, 20*app.height/40, anchor="se", text="Plays", font="Helvetica 18")
    canvas.create_text(4.5*app.width/5, 20*app.height/40, anchor="sw", text="Length", font="Helvetica 18")
    canvas.create_rectangle(3*app.width/8, 3*app.height/12, 5*app.width/8, 5*app.height/12, outline="#FFA8B7", fill="#FFA8B7")
    canvas.create_text(app.width/2, 4*app.height/12, text="Export to Spotify", font="Helvetica 20")

    canvas.create_text(app.width/6, 8.5*app.height/24, anchor="se", text=f"Playlist Name: ", font="Helvetica 14")
    canvas.create_rectangle(app.width/6, 7.5*app.height/24, app.width/3, 8.5*app.height/24, outline="black", fill="white")
    canvas.create_text(app.width/6 +5, 8.5*app.height/24, anchor="sw", text=app.playlistName, font="Helvetica 14")

def export(app):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=app.SPOTIFY_KEY,
                                               client_secret=app.SPOTIFY_SECRET,
                                               redirect_uri="https://www.google.com/",
                                               scope="playlist-modify-public"))
    sp.user_playlist_create(app.SPOTIFY_USER, app.playlistName, public=True, collaborative=False, 
                            description="Automatically generated using Spotilast by Devan Grover.")
    playlists = sp.user_playlists(app.SPOTIFY_USER, limit=50)
    playlistID = ""
    for i in playlists["items"]:
        if(i["name"] == app.playlistName):
            playlistID = i["id"]
    
    app.erroredTracks = []
    for i in range(math.ceil(len(app.selectedSongs)/100)):
        trackIDset = []
        for p in range(0, 100):
            if(i*100 + p < len(app.selectedSongs)):
                trackName = app.selectedSongs[i*100 + p]["name"]
                trackArtist = app.selectedSongs[i*100 + p]["artist"]["name"]
                searchResults = []
                searchQuery = f"track:{trackName} artist:{trackArtist}"
                searchResults = sp.search(q=searchQuery, type="track", limit=2)
                print(searchResults)
                if(len(searchResults["tracks"]["items"]) == 0): 
                    app.erroredTracks.append(app.selectedSongs[i*100 + p])
                    continue
            else:
                break
            trackIDset.append(searchResults["tracks"]["items"][0]["id"])
        if(trackIDset != []):
            sp.user_playlist_add_tracks(app.SPOTIFY_USER, playlist_id=playlistID, tracks=trackIDset, position=None)
    app.selectedSongs = []
    app.mode="finalMode"

def exportMode_mousePressed(app, event):
    x, y = event.x, event.y
    if(y >= 0 and y <= app.height/6):
        if(x >= app.width/4 and x <= 2* app.width/4):
            app.mode = "pieChartMode"
        elif(x >= 2 * app.width/4 and x <= 3 * app.width/4):
            app.mode = "queryMode"
        elif(x >= 0 and x <= app.width/4):
            app.mode = "searchMode"
    if(mouseInBox(x, y, app.width-40, app.height-30, app.width-20, app.height-17.321)):
        if(app.exportPage < math.ceil(len(app.selectedSongs)/5)-1):
            app.exportPage += 1
    elif(mouseInBox(x, y, app.width-40, 22*app.height/40, app.width-20, 22*app.height/40+12.7)):
        if(app.exportPage > 0):
            app.exportPage -= 1
    if(mouseInBox(x, y, 3*app.width/8, 3*app.height/12, 5*app.width/8, 5*app.height/12) and app.playlistName != "" and app.selectedSongs != []):
        app.mode = "finalMode"
        export(app)
    # https://www.geeksforgeeks.org/ways-sort-list-dictionaries-values-python-using-lambda-function/
    if(mouseInBox(x, y, 10, app.height/2-30, 40, app.height/2)):
        if(app.selectionLastSorted[1] == "name"):
            if(app.selectionLastSorted[0] == 0):
                app.selectionLastSorted = (1, "name")
                app.selectedSongs = sorted(app.selectedSongs, key=lambda k: k["name"].lower(), reverse=True)
            else:
                app.selectionLastSorted = (0, "name")
                app.selectedSongs = sorted(app.selectedSongs, key=lambda k: k["name"].lower(), reverse=False)
        else:
            app.selectionLastSorted = (0, "name")
            app.selectedSongs = sorted(app.selectedSongs, key=lambda k: k["name"].lower(), reverse = False)
    elif(mouseInBox(x, y, 1.5*app.width/5, app.height/2-30, 1.5*app.width/5+60, app.height/2)):
        if(app.selectionLastSorted[1] == "artist"):
            if(app.selectionLastSorted[0] == 0):
                app.selectionLastSorted = (1, "artist")
                app.selectedSongs = sorted(app.selectedSongs, key=lambda k: k["artist"]["name"].lower(), reverse=True)
            else:
                app.selectionLastSorted = (0, "artist")
                app.selectedSongs = sorted(app.selectedSongs, key=lambda k: k["artist"]["name"].lower(), reverse=False)
        else:
            app.selectionLastSorted = (0, "artist")
            app.selectedSongs = sorted(app.selectedSongs, key=lambda k: k["artist"]["name"].lower(), reverse = False)
    elif(mouseInBox(x, y, 2.75*app.width/5, app.height/2-30, 2.75*app.width/5+70, app.height/2)):
        if(app.selectionLastSorted[1] == "album"):
            if(app.selectionLastSorted[0] == 0):
                app.selectionLastSorted = (1, "album")
                app.selectedSongs = sorted(app.selectedSongs, key=lambda k: k["album"].lower(), reverse=True)
            else:
                app.selectionLastSorted = (0, "album")
                app.selectedSongs = sorted(app.selectedSongs, key=lambda k: k["album"].lower(), reverse=False)
        else:
            app.selectionLastSorted = (0, "album")
            app.selectedSongs = sorted(app.selectedSongs, key=lambda k: k["album"].lower(), reverse = False)
    elif(mouseInBox(x, y, 4.25*app.width/5-65, app.height/2-30, 4.25*app.width/5, app.height/2)):
        if(app.selectionLastSorted[1] == "playcount"):
            if(app.selectionLastSorted[0] == 0):
                app.selectionLastSorted = (1, "playcount")
                app.selectedSongs = sorted(app.selectedSongs, key=lambda k: int(k["playcount"]), reverse=True)
            else:
                app.selectionLastSorted = (0, "playcount")
                app.selectedSongs = sorted(app.selectedSongs, key=lambda k: int(k["playcount"]), reverse=False)
        else:
            app.selectionLastSorted = (0, "playcount")
            app.selectedSongs = sorted(app.selectedSongs, key=lambda k: int(k["playcount"]), reverse = False)
    elif(mouseInBox(x, y, 4.5*app.width/5, app.height/2-30, 4.5*app.width/5 +75, app.height/2)):
        if(app.selectionLastSorted[1] == "duration"):
            if(app.selectionLastSorted[0] == 0):
                app.selectionLastSorted = (1, "duration")
                app.selectedSongs = sorted(app.selectedSongs, key=lambda k: int(k["duration"]), reverse=True)
            else:
                app.selectionLastSorted = (0, "duration")
                app.selectedSongs = sorted(app.selectedSongs, key=lambda k: int(k["duration"]), reverse=False)
        else:
            app.selectionLastSorted = (0, "duration")
            app.selectedSongs = sorted(app.selectedSongs, key=lambda k: int(k["duration"]), reverse = False)

    try:
        if(mouseInBox(x, y, 0, 20*app.height/40, app.width - 45, 24*app.height/40)):
            app.selectedSongs.remove(app.selectedSongs[app.exportPage*5])
        elif(mouseInBox(x, y, 0, 24*app.height/40, app.width - 45, 28*app.height/40)):
            app.selectedSongs.remove(app.selectedSongs[app.exportPage*5 + 1])
        elif(mouseInBox(x, y, 0, 28*app.height/40, app.width - 45, 32*app.height/40)):
            app.selectedSongs.remove(app.selectedSongs[app.exportPage*5 + 2])
        elif(mouseInBox(x, y, 0, 32*app.height/40, app.width - 45, 36*app.height/40)):
            app.selectedSongs.remove(app.selectedSongs[app.exportPage*5 + 3])
        elif(mouseInBox(x, y, 0, 36*app.height/40, app.width - 45, 40*app.height/40)):
            app.selectedSongs.remove(app.selectedSongs[app.exportPage*5 + 4])
    except:
        pass
    
def exportMode_keyPressed(app, event):
    key = event.key
    if(len(key) == 1 or key == "backspace" or key == "Backspace" or key == "space" or key == "Space"):
        if(len(key) == 1 and len(app.playlistName) < 20):
            app.playlistName += key
        elif(key == "space" or key == "Space"):
            app.playlistName += " "
        elif(key == "backspace" or key == "Backspace"):
            app.playlistName = app.playlistName[:-1]

##########################################
# Final Screen
##########################################

def finalMode_redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill="#FFC0CB", outline="#FFC0CB")
    for i in range(app.finalPage*5, app.finalPage*5+5):
        if(i < len(app.erroredTracks)):
            fill="black"
            canvas.create_text(10, (22+(i%5)*4)*app.height/40, text=app.erroredTracks[i].get("name"), anchor="w", fill=fill, font="Helvetica 12")
            canvas.create_text(2.75*app.width/5, (22+(i%5)*4)*app.height/40, text=app.erroredTracks[i].get("album"), anchor="w", font="Helvetica 12")
            canvas.create_text(1.5*app.width/5, (22+(i%5)*4)*app.height/40, text=app.erroredTracks[i].get("artist").get("name"), anchor="w", font="Helvetica 12")
            canvas.create_text(4.25*app.width/5, (22+(i%5)*4)*app.height/40, text=app.erroredTracks[i].get("playcount"), anchor="w", font="Helvetica 12")
            tot = int(app.erroredTracks[i].get("duration"))
            secs = tot%60
            mins = tot//60
            if(secs < 10):
                secs = f"0{secs}"
            canvas.create_text(4.5*app.width/5, (22+(i%5)*4)*app.height/40, text=f"{mins}:{secs}", anchor="w", font="Helvetica 12")
    canvas.create_polygon(app.width-40, app.height-30, app.width-20, app.height-30, app.width-30, app.height-17.321)
    canvas.create_polygon(app.width-40, 22*app.height/40+12.7, app.width-20, 22*app.height/40+12.7, app.width-30, 22*app.height/40)
    canvas.create_line(0,20*app.height/40, app.width, 20*app.height/40)
    canvas.create_line(0,24*app.height/40, app.width, 24*app.height/40)
    canvas.create_line(0,28*app.height/40, app.width, 28*app.height/40)
    canvas.create_line(0,32*app.height/40, app.width, 32*app.height/40)
    canvas.create_line(0,36*app.height/40, app.width, 36*app.height/40)
    canvas.create_text(10, 20*app.height/40, anchor="sw", text="Title:", font="Helvetica 18")
    canvas.create_text(2.75*app.width/5, 20*app.height/40, anchor="sw", text="Album", font="Helvetica 18")
    canvas.create_text(1.5*app.width/5, 20*app.height/40, anchor="sw", text="Artist", font="Helvetica 18")
    canvas.create_text(4.25*app.width/5, 20*app.height/40, anchor="se", text="Plays", font="Helvetica 18")
    canvas.create_text(4.5*app.width/5, 20*app.height/40, anchor="sw", text="Length", font="Helvetica 18")
    canvas.create_text(app.width/2, 16.5*app.height/40, anchor="n", font="Helvetica 12",
        text="The following songs were unable to be added to the Spotify playlist")
    canvas.create_rectangle(2*app.width/10, 6.5*app.height/40, 4*app.width/10, 12.5*app.height/40, fill="#FFA8B7", outline="#FFA8B7")
    canvas.create_rectangle(6*app.width/10, 6.5*app.height/40, 8*app.width/10, 12.5*app.height/40, fill="#FFA8B7", outline="#FFA8B7")
    canvas.create_text(3*app.width/10, 9.5*app.height/40, text="Back", font="Helvetica 22")
    canvas.create_text(7*app.width/10, 9.5*app.height/40, text="Login", font="Helvetica 22")


def finalMode_mousePressed(app, event):
    x, y = event.x, event.y
    if(mouseInBox(x, y, app.width-40, app.height-30, app.width-20, app.height-17.321)):
        if(app.finalPage < math.ceil(len(app.erroredTracks)/5)-1):
            app.finalPage += 1
    elif(mouseInBox(x, y, app.width-40, 22*app.height/40, app.width-20, 22*app.height/40+12.7)):
        if(app.finalPage > 0):
            app.finalPage -= 1
    if(mouseInBox(x, y, 2*app.width/10, 6.5*app.height/40, 4*app.width/10, 12.5*app.height/40)):
        app.finalPage = 0
        app.drawPie, app.drawBar, app.drawLine = False, False, False
        app.encodedPieData, app.encodedlineData, app.encodedBarData = {}, {}, {}
        app.pieData, app.lineData, app.barData, app.erroredTracks = [], [], [], []
        app.maxLine = 0
        app.linePoints = 0
        app.selectedPie = False
        app.selectedBar = False
        app.selectedLine = False
        app.pieSettings = ("", "songs", "7day")
        app.barSettings = ("", "songs", "7day")
        app.lineSettings = ("", "songs", "7day")
        app.playlistName = ""
        app.resultsLastSorted = (0, "plays")
        app.selectionLastSorted = (0, "")
        app.results = []
        app.selectedSongs = []
        app.searchPage = 0
        app.exportPage = 0
        app.currentlySelectedBox = ""
        app.searchQueryFontSize = 18
        app.searchQuery = ""
        app.filter = "song"
        app.loaded = False
        app.runGetData = False
        app.getDataTracker = False
        app.songs = []
        app.mode = "searchMode"
    elif(mouseInBox(x, y,6*app.width/10, 6.5*app.height/40, 8*app.width/10, 12.5*app.height/40)):
        appStarted(app)

##########################################
# App
##########################################

def appStarted(app):
    app.timeQuery = ""
    app.finalPage = 0
    app.drawPie, app.drawBar, app.drawLine = False, False, False
    app.colors = ["#8B008B", "#FF4500", "#FFFF00", "#00FF7F", "#FF1493", "#8A2BE2",
                  "#7CFC00", "#696969", "#556B2F", "#800000", "#483D8B", "#3CB371",
                  "#000080", "#9ACD32", "#DAA520", "#00FFFF", "#00BFFF", "#0000FF", 
                  "#D8BFD8", "#FF00FF", "#1E90FF", "#DB7093", "#EEE8AA",  "#FFA07A", "#EE82EE"]
    app.encodedPieData, app.encodedlineData, app.encodedBarData = {}, {}, {}
    app.pieData, app.lineData, app.barData, app.erroredTracks = [], [], [], []
    app.maxLine = 0
    app.linePoints = 0
    app.queryList = []
    app.selectedPie = False
    app.selectedBar = False
    app.selectedLine = False
    app.pieSettings = ("", "songs", "7day")
    app.barSettings = ("", "songs", "7day")
    app.lineSettings = ("", "songs", "7day")
    app.playlistName = ""
    app.resultsLastSorted = (0, "plays")
    app.selectionLastSorted = (0, "")
    app.results = []
    app.selectedSongs = []
    app.querySelected = False
    app.searchPage = 0
    app.exportPage = 0
    app.queryPage = 0
    app.currentlySelectedBox = ""
    app.searchQueryFontSize = 18
    app.searchQuery = ""
    app.filter = "song"
    app.loaded = False
    app.runGetData = False
    app.getDataTracker = False
    app.songs = []
    app.LASTFM_URL = "http://ws.audioscrobbler.com/2.0/"
    app.LASTFM_USER, app.LASTFM_KEY= "", "45be5b99eb4c52bf0bf2175fdf56b820"
    app.SPOTIFY_USER, app.SPOTIFY_KEY, app.SPOTIFY_SECRET = "devg1", "ce96c423a54744b9844950a4382874ca", "69c65f35deeb44349f87d385662ecb57"
    app.albumQuery, app.artistQuery, app.playsQuery, app.durationQuery, app.dateQuery, app.titleQuery = "", "", "", "", "", ""
    app.mode = 'splashScreenMode'
   

runApp(width=1280, height=720)