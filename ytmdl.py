'''* ------------------------------------------------
   * A simple script to download songs in mp3 format
   * from Youtube. It then asks the user for the song name
   * which is then searched in itunes for metadata.
   * -------------------------------------------------
   * Deepjyoti Barman
   * deepjyoti30@github.com'''

from __future__ import unicode_literals
import youtube_dl
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TCON, TRCK
from mutagen.mp3 import MP3
import os
import glob
from pathlib import Path
import itunespy
import sys
import shutil

# Define colors
class bcolors:
    CYAN = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# The home dir
HOME_DIR = str(Path.home())

# The temp song dir
SONG_DIR = os.path.join(HOME_DIR, 'Music', 'temp')

# The name that the song will be saved with
SONG_NAME_TO_SAVE = ''

#-----------Print----------------------
def PREPEND(state):
    # State 1 is for ok
    # State 2 is for notok

    print(bcolors.BOLD,end='')
    if state == 1:
        print(bcolors.OKGREEN, end='')
    elif state == 2:
        print(bcolors.FAIL, end='')
    else:
        pass

    print(' ==> ',end='')
    print(bcolors.ENDC, end='')

#--------------------------------------


def GRAB_SONG(link):
    ydl_opts = {
        'format' : 'bestaudio',
        'quiet' : True,
        'outtmpl' : os.path.join(SONG_DIR, '%(title)s.%(ext)s'),
        'postprocessors':[{
            'key' : 'FFmpegExtractAudio',
            'preferredcodec' :  'mp3'
        }]
    }

    # Download the song with youtube-dl
    try:
        ydl = youtube_dl.YoutubeDL(ydl_opts)
        ydl.download([link])
        return True
    except:
        return False

#-----------------------tag----------------------

def getData(SONG_NAME):
    # Try to get the song data from itunes
    try:
        SONG_INFO = itunespy.search_track(SONG_NAME)
        return SONG_INFO
    except:
        return False

def getChoice(SONG_INFO):
    # Print 5 of the search results
    # In case less, print all

    PREPEND(1)
    print('Choose One')

    results = len(SONG_INFO)
    count = 0

    if results > 5:
        results = 5

    while count != results:
        print(' [' + str(count+1) + '] ',end='')
        print(SONG_INFO[count].track_name + ' by ' + SONG_INFO[count].artist_name)
        
        count += 1

    while True:  
        PREPEND(1)
        choice = input('Enter Choice [a valid choice] ')
        if choice <= str(results + 1) and choice > str(0):
            break 

    choice = int(choice)
    choice -= 1
    return choice

def setData(SONG_INFO):

    try:
        # If more than one choice then call getChoice
        if len(SONG_INFO) > 1:
            option = getChoice(SONG_INFO)
        else:
            option = 0
        
        SONG_PATH = glob.glob(os.path.join(SONG_DIR,'*mp3'))

        #SONG_PATH = os.path.basename(SONG_PATH[0])

        audio = MP3(SONG_PATH[0], ID3=ID3)
        data = ID3(SONG_PATH[0])

        # If tags are not present then add them
        try:
            audio.add_tags()
        except:
            pass

        audio.save()

        option = int(option)

        data.add(TIT2(encoding=3, text=SONG_INFO[option].track_name))
        data.add(TPE1(encoding=3, text=SONG_INFO[option].artist_name))
        data.add(TALB(encoding=3, text=SONG_INFO[option].collection_name))
        data.add(TCON(encoding=3, text=SONG_INFO[option].primary_genre_name))
        data.add(TRCK(encoding=3, text=str(SONG_INFO[option].track_number)))

        data.save()

        SONG_NAME_TO_SAVE = SONG_INFO[option].track_name + '.mp3'

        # Rename the downloaded file
        os.rename(SONG_PATH[0], os.path.join(SONG_DIR, SONG_NAME_TO_SAVE))

        PREPEND(1)
        print('TITLE: ' + SONG_INFO[option].track_name)
        PREPEND(1)
        print('ARITST: ' + SONG_INFO[option].artist_name)
        PREPEND(1)
        print('ALBUM: ' + SONG_INFO[option].collection_name)
        PREPEND(1)
        print('GENRE: ' + SONG_INFO[option].primary_genre_name)
        PREPEND(1)
        print('TRACK NO: ' + str(SONG_INFO[option].track_number))

        return True
    except:
        return False

def cleanup():
    # Move the song from temp to $HOME/Music dir
    try: 
        SONG = glob.glob(os.path.join(SONG_DIR, '*mp3'))
        SONG = SONG[0]

        SONG_NAME = os.path.basename(SONG)
        shutil.move(SONG, os.path.join(HOME_DIR, 'Music', SONG_NAME))

        return True
    except:
        return False

#-----------------------------------------------

def main():

    if len(sys.argv) != 3:
        print(bcolors.WARNING,end='')
        print(' Usage: ',end='')
        print(sys.argv[0] + ' [URL] [TRACK NAME]')
        print(bcolors.ENDC,end='')
        sys.exit(0)

    PREPEND(1)
    print('Downloading the song to ' + SONG_DIR)
    if not GRAB_SONG(sys.argv[1]):
        PREPEND(2)
        print('Something went wrong while downloading!\a')
        sys.exit(0)
    else:
        PREPEND(1)
        print('Downloaded!')

    PREPEND(1)
    print('Getting song data...')

    TRACK_INFO = getData(sys.argv[2])

    if TRACK_INFO == False:
        PREPEND(2)
        print('Something went wrong while getting data!\a')
        sys.exit(0)
    elif len(TRACK_INFO) == 0:
        PREPEND(2)
        print('No data was found!\a')
        sys.exit(0)
    else:
        PREPEND(1)
        print('Data downloaded!')

    PREPEND(1)
    print('Setting data...')

    if not setData(TRACK_INFO):
        PREPEND(2)
        print('Something went wrong while writing data!\a')
        sys.exit(0)

    PREPEND(1)
    print('Moving to Music directory...')

    if not cleanup():
        PREPEND(2)
        print('Something went wrong while moving!\a')
        sys.exit(0)
    else:
        PREPEND(1)
        print('Done!')
    

main()