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

class NoSongsFound(Exception):
    """
    Creates an exception if no songs are found.
    """
    pass

class CreatePlaylist:

    def __init__(self):
        self._tracklist = []
        self._title = ''
        self._length = 0
        pass

    def get_tracklist(self):
        return self._tracklist
    
    def get_length(self):
        return self._length
    
    def get_title(self):
        return self._title

    # Step 1: Log into YouTube 
    def get_youtube_client(self):
        pass

    # Step 2: Grab our liked videos
    def get_songs_youtube(self, url, PATH="C:\Program Files (x86)\chromedriver-win32\chromedriver.exe", option1='--headless=new'):
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
        # load page
        driver = webdriver.Chrome(executable_path=PATH, options=options)
        try:
            driver.get(url)
            driver.maximize_window()
        except Exception as e:
            print("URL failed to load.", e)

        # expand the description
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "expand")))
            driver.find_element(By.ID, 'expand').send_keys(Keys.RETURN)
        except Exception as e:
            print("Failed to expand description", e)

        # bring comments into viewport
        try:
            comment = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="content-text"]')))
            comment.location_once_scrolled_into_view
        except Exception as e:
            print("Failed to go to first comment.", e)

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')


        # if get_num_songs_music_desc() >= get_num_songs_tracklist_desc():
        #     get_songs_music_desc()

        def find_title(soup = soup, tag='h1', class_name='style-scope ytd-watch-metadata'):
            # capture title of video - to be used as playlist title
            try:
                playlist_title = soup.find(tag, {'class': class_name}).text
            except Exception as e:
                print(e, "Title not found")
                return ""
            
            playlist_title = playlist_title.strip('\n')
            cant_contain_list = ['/', '\\', '|', '<', '>', '*', '?', '"', ":"]
            for nono in cant_contain_list:
                playlist_title = playlist_title.replace(nono, '')

            self._title = playlist_title
            return playlist_title

        def get_num_songs_music_desc(soup=soup, tag='yt-formatted-string', class_name='style-scope ytd-channel-name', id_name='text'):
            """
            Looks for the number of songs that would be found in the music
            banner portion of the description and returns and integer. 
            """
            # tag='div', class_name='style-scope ytd-expander', id_name='content'
            try:
                find_songs = soup.find_all(tag, {
                    'class': class_name,
                    'id': id_name
                    })
            except Exception as e:
                print(e, "No songs found in video banner.")
                return 0
            
            text_holder = []
            song_count = []
            for song in find_songs:
                text_holder.append(str(song.text))
            # find the statement 'Song 1 of x' where x is the total number of songs
            for song in text_holder:
                if 'Song 1 of' in song:
                    if song not in song_count:
                        song_count.append(song)
                        break
            
            # remove whitespace and target last index as "num songs" integer
            if song_count is not None:
                num_songs_str = song_count[0].split(' ')
                num_songs = int(num_songs_str[-1])
            
            if num_songs is None:
                num_songs = 0
                return num_songs
            
            return num_songs
        
        def get_songs_tracklist_desc(soup=soup, tag='span', class_name='yt-core-attributed-string--link-inherit-color'):
            """
            Looks for the number of songs that would be found in a custom
            tracklist in the description and returns and integer.             
            """
            try:
                find_songs = soup.find_all(tag, {
                    'class': class_name
                    })
                
            except Exception as e:
                print(e, "Video description not found.")
                return 0
            
            text_holder = []
            text_transfer_list = []
            for song in find_songs:
                text_holder.append(str(song.text))
            index_count = 0
            for text in text_holder:
                if index_count > 0:
                    index_count += 1
                    if index_count % 2 == 0:
                        if text not in text_transfer_list:
                            if 'intro' not in text.lower() and text.strip() != '':
                                text_transfer_list.append(text.strip())
                    if (index_count % 2 != 0) and (':' not in text):
                        break
                if '0:00' in text:
                    index_count += 1
            
            cant_contain_list = ('/', '\\', '|', '<', '>', '*', '?', '"', ":", " - ", "-", "  ")
            text_transfer_list = "#".join(text_transfer_list)
            
            for nono in cant_contain_list:
                text_transfer_list = text_transfer_list.replace(nono, ' ')
            text_transfer_list = text_transfer_list.split('#')
            for text in text_transfer_list:
                text.strip()
                        
            return text_transfer_list

        def get_songs_music_desc(num_songs, soup=soup):
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
            # text file saved in repo location
            custom_desc_tracklist = [artist_holder[i] + ' ' + song_holder[i] for i in range(len(song_holder))]

            
            return self._tracklist
        
        def get_songs_comment(soup=soup, tag='yt-formatted-string', id_name='content-text'):
            """
            Looks for the the tracklist in Top 3 comments and returns a list of 'song + artist' strings.             
            """
            text_holder = []
            try:
                find_songs = soup.find_all(tag, {
                    'id': id_name
                    })
                
            except Exception as e:
                print(e, "Comments not found.")
                return 0
            
            for val in range(10):
                comment = find_songs[val]
                if '0:00' in comment.text and 'Sign in' not in comment.text:
                    all_tracks = comment.span
                    start_flag = 0
                    for track in all_tracks.next_siblings:
                        if start_flag == 1:
                            text_holder.append(track.text)
                            start_flag = 0
                        elif start_flag == 0 and ':' in track.text:
                            start_flag = 1
                    break

            for text in text_holder:
                text.strip()
                        
            return text_holder

        # ---------------------------------------------
        # script that scrapes URL and creates tracklist
        # ---------------------------------------------
        #   get title
        playlist_title = find_title()

        #   get tracklist from 1 of 3 sources - will be source with most tracks
        description_tracklist = get_songs_tracklist_desc()
        auto_tracklist_num = get_num_songs_music_desc()
        comment_tracklist = get_songs_comment()
        if len(description_tracklist) >= auto_tracklist_num and len(description_tracklist) >= len(comment_tracklist):
            self._tracklist = description_tracklist
            self._length = len(description_tracklist)
            driver.quit()
        elif len(comment_tracklist) >= auto_tracklist_num:
            self._tracklist = comment_tracklist
            self._length = len(comment_tracklist)
            driver.quit()
        else:
            self._tracklist = get_songs_music_desc(auto_tracklist_num)
            self._length = auto_tracklist_num
            driver.quit()

        #   save title and tracklist in txt file
        playlist_title = str(playlist_title) + '.txt'
        with open(playlist_title, 'w', encoding='utf-8') as outfile:
            for track in self._tracklist:
                outfile.write(f'{track}\n')

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

if __name__ == "__main__":
    playlist = CreatePlaylist()
    # utube_url = input("Enter YouTube URL:\n")
    playlist.get_songs_youtube('https://www.youtube.com/watch?v=3CeRaSBesiw')
    playlist.get_songs_youtube('https://www.youtube.com/watch?v=fsakyvtqETA')
    playlist.get_songs_youtube('https://www.youtube.com/watch?v=Zz6oob45faU')
