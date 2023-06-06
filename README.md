# youtube-to-spotify
Takes your favorite, multi-artist mixes from YouTube, pulls out the songs and artist, and adds them to a Spotify playlist.

This is an ONGOING project and is by no means complete.
For an example of a target video, visit: https://www.youtube.com/watch?v=s-jtdKjzQaE
___________________________________________________________________________________________________________
This project is broken down into 2 main components:
1. Webscraping the YouTube video for artists/songs
2. Adding the artists/songs to a custom Spotify playlist

___________________________________________________________________________________________________________
1. Webscraping the Youtube video for artists/songs

Status: Learning how to work with Selenium module for web automation and accessing content behind buttons.

A. Artists/Songs can be stored in 4 different locations:
  1. Tracklist in the description
  2. Artist and Song element in the description (information not available through YouTube API yet)
  3. Video chapters descriptions
  4. Tracklist in the comments
B. Selenium module finds and clicks the 'Show More' button and, in the case of A.2 the 'next' button (>).
C. BeautifulSoup and Request Module allow distinct tags and class_ info to be searched for and parsed
  1. Tracklists (A.1 and A.3) are identified by the word 'tracklist' and timestamps, after which is the artist/song info
  2. Elements (A.2 and A.3) are uniquely identifiable but do not often have the full list
D. Build either a list with the artist and song mixed together or a hash table with artist (key) and song (value).
E. Assign the video's title to a variable

___________________________________________________________________________________________________________
2. Adding the artists/songs to a custom Spotify playlist
 
Status: API token can be created. Learning how to interact with API.

A. Access user credentials and generate token
B. Create a Spotify playlist with the YouTube video's title as the name
B. Iterate through the list or hash table contents and use as a search query
C. Add the top result to the new playlist
D. Repeat for all items in list
