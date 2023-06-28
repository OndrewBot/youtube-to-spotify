# Step 1: Log into YouTube 
# Step 2: Grab songs from the video
# Step 3: Create a custom playlist
# Step 4: Search for the song
# Step 5: Add song into new Spotify playlist

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from access_token import get_token
import json

class NoSongsFound(Exception):
    """
    Creates an exception if no songs are found.
    """
    pass

class CreatePlaylist:

    def __init__(self):
        self._tracklist = {}
        pass

    def get_tracklist(self):
        return self._tracklist

    # Step 1: Log into YouTube 
    def get_youtube_client(self):
        pass

    # Step 2: Grab our liked videos
    def get_songs_youtube(self, url, PATH="C:\Program Files (x86)\chromedriver.exe", option1='--headless=new'):
        """
        Loads the webpage. Finds the number of songs in the video. Looks if a tracklist is in the description
            or in the top 5 comments. Also looks to see if the description has a 'music' section with song/artist
            info. The location that contains more songs will be used to create tracklist. If both locations contain
            the same number, default is the tracklist.
        Requirements: Chromedriver, bs4, selenium
        :param: url    -  the address of the youtube video
        :param: PATH   -  the local address of chromedriver.exe as string
                        defaults to "C:\Program Files (x86)\chromedriver.exe"
        :param: option1-  webdriver option 1(3)
                        defaults to '--headless=new'
        """
        options = webdriver.ChromeOptions()
        options.add_argument(option1)
        

        driver = webdriver.Chrome(executable_path=PATH, options=options)
        driver.get(url)
        driver.maximize_window()
        time.sleep(4)

        # expand the description and let it load
        search = driver.find_element(By.ID, 'expand')
        search.send_keys(Keys.RETURN)
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        # capture title of video - to be used as playlist title
        playlist_title = soup.find('h1', {'class': 'style-scope ytd-watch-metadata'}).text
        playlist_title = playlist_title.strip('\n')
        cant_contain_list = ['/', '\\', '|', '<', '>', '*', '?', '"', ":"]
        for nono in cant_contain_list:
            playlist_title = playlist_title.replace(nono, '')

        # ----------------------------------------------------------
        # determine the number of songs in the video via Music section
        # ----------------------------------------------------------
        def get_num_songs_music_desc():
            """
            Looks for the number of songs that would be found in the music
            description and returns and integer. 
            """
            find_songs = soup.find_all('yt-formatted-string', {
                'class': 'style-scope ytd-channel-name',
                'id': 'text'
                })
            text_holder = []
            song_count = []
            for song in find_songs:
                text_holder.append(str(song.text))
            # find the statement 'Song 1 of x' where x is the total number of songs
            for song in text_holder:
                if 'Song 1 of' in song:
                    if song not in song_count:
                        song_count.append(song)
            num_songs_str = song_count[0].split(' ')
            num_songs = int(num_songs_str[-1])
            
            if num_songs is None:
                num_songs = 0
                return num_songs
            return num_songs

        def get_songs_music_desc(num_songs):
            """
            Find and collect the song and artist name from the music section
            in the description. Clicks the 'right-arrow-button' a number of times
            to collect all of the song-artist info. Albums are not collected.
            """
            # move MUSIC section in description into view
            js_code_next = 'arguments[0].scrollIntoView();'
            move_right = driver.find_element(By.ID, "right-arrow-button")
            driver.execute_script(js_code_next, move_right)

            # collect songs
            all_songs = soup.find_all('span', {
                'id': 'video-title',
                'class': 'style-scope ytd-compact-video-renderer style-scope ytd-compact-video-renderer'
                })
            song_holder = []
            for song in all_songs:
                song_holder.append(str(song.text))
            song_holder = [song.strip() for song in song_holder[0:num_songs]]

            # collect artist and click the right button
            artist_holder = []
            artist = soup.find('yt-formatted-string', {
                    'id': 'default-metadata',
                    'class': 'style-scope ytd-info-row-renderer'
                    })
            artist_holder.append(str(artist.text))
            for _ in range(num_songs-1):
                actions = ActionChains(driver)
                actions.move_to_element(move_right)
                actions.click(move_right)
                actions.perform()
                time.sleep(.5)
                html = driver.page_source       # page source must be reloaded into soup due to dynamics
                soup = BeautifulSoup(html, 'lxml')
                artist = soup.find('yt-formatted-string', {
                    'id': 'default-metadata',
                    'class': 'style-scope ytd-info-row-renderer'
                    })
                artist_holder.append(str(artist.text))
        
            # create the tracklist and add it to a text file
            self._tracklist = {song_holder[i]: artist_holder[i] for i in range(len(song_holder))}  
            # key is song: value is artist
            playlist_title = str(playlist_title) + '.txt'
            with open(playlist_title, 'w', encoding='utf-8') as outfile:
                for track in self._tracklist:
                    outfile.write(f'{track} by {self._tracklist[track]}\n')

            driver.quit()
            
            return self._tracklist
        
        def num_songs_tracklist_desc():
            """
            
            """
            pass

        def num_songs_tracklist_comment():
            """
            
            """

    # Step 4: Create a custom playlist
    def create_playlist(self):
        token = get_token()
        pass

    # Step 4: Search for the song
    def get_spotify_url(self):
        pass

    # Step 5: Add song into new Spotify playlist
    def add_song_to_playlist(self):
        pass

#-------------------------------------------------------------------------------------------

playlist = CreatePlaylist()
playlist.get_songs_youtube('https://www.youtube.com/watch?v=Zz6oob45faU')
