# youtube-to-spotify
Takes your favorite, multi-artist mixes from YouTube, pulls out the songs and artist, and adds them to a Spotify playlist.

This is an ONGOING project and is by no means complete.
For an example of a target video, visit: https://www.youtube.com/watch?v=s-jtdKjzQaE
___________________________________________________________________________________________________________
This project is broken down into 2 main components:
1. Webscraping the YouTube video for artists/songs
2. Adding the artists/songs to a custom Spotify playlist

___________________________________________________________________________________________________________
Webscraping the Youtube video for artists/songs:

Status: Learning how to work with Selenium module for web automation and accessing content behind buttons.

1. Artists/Songs can be stored in 4 different locations:
  A. Tracklist in the description
  B. Artist and Song element in the description (information not available through YouTube API yet)
  C. Video chapters descriptions
  D. Tracklist in the comments
2. Selenium module finds and clicks the 'Show More' button and, in the case of A.2 the 'next' button (>).
3. BeautifulSoup and Request Module allow distinct tags and class_ info to be searched for and parsed
  A. Tracklists (A.1 and A.3) are identified by the word 'tracklist' and timestamps, after which is the artist/song info
  B. Elements (A.2 and A.3) are uniquely identifiable but do not often have the full list
4. Build either a list with the artist and song mixed together or a hash table with artist (key) and song (value).
5. Assign the video's title to a variable

___________________________________________________________________________________________________________
Adding the artists/songs to a custom Spotify playlist:
 
Status: API token can be created. Learning how to interact with API.

1. Access user credentials and generate token
2. Create a Spotify playlist with the YouTube video's title as the name
3. Iterate through the list or hash table contents and use as a search query
4. Add the top result to the new playlist
5. Repeat for all items in list
