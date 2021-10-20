import numpy as np
import pydub
import pyaudio
import warnings
import sys
import os
from bokeh.io import show
from bokeh.plotting import figure 

# This class defines an AudioS object that stores the name of an audio track and its metadata. 
# It also contains all the functions used to read/record/play audio, update playback rate,
# and saving the object to file.

class AudioS():
    
    # Initializing AudioS object.
    
    def __init__(self, process='m'):
        self.songname = ''
        self.framerate = []
        if process == 'a':
            self.ask_user()
        elif process == 'm':
            pass
        else:
            if input('Enter "a" for default scratching or "m" to proceed manually: ') == 'a':
                self.ask_user()
            else:
                sys.exit('''Error: Incorrect entry.''')
                
    def ask_user(self):
        audio_type = input('Enter "f" to read from audio file or "r" to record audio: ')
        if audio_type == 'f':
            filename = input('Enter the filename you want to read (excluding the extension): ')
            self.songname = filename
            if input('Do you want to show all plots? Enter "y" or "n": ') == 'y':
                plot = True
            else:
                plot = False
            channels, self.framerate = self.read_audiofile(plot, filename)

        elif audio_type == 'r':
            filename = input('Enter a name for the recording:')
            if input('Do you want to show all plots? Enter "y" or "n": ') == 'y':
                plot = True
            else:
                plot = False
            channels, self.framerate = self.record_audiofile(plot, filename)
            
        else:
            sys.exit('''Error: Incorrect entry. Enter "f" to read an audio file or 
                     "r" to record''')
            
    # Read audio file using pydub and plot signal.
    # The audio file has to be .mp3 format
    def read_audiofile(self, plot, filename):
        songdata = []  # Empty list for holding audio data
        channels = []  # Empty list to hold data from separate channels
        filename = os.getcwd() + '/songs/' + filename
        audiofile = pydub.AudioSegment.from_file(filename + '.mp3')
        self.songname = os.path.split(filename)[1]
        songdata = np.frombuffer(audiofile._data, np.int16)
        for chn in range(audiofile.channels):
            channels.append(songdata[chn::audiofile.channels])  # separate signal from channels
        framerate = audiofile.frame_rate
        channels = np.sum(channels, axis=0) / len(channels)  # Averaging signal over all channels
        # Plot time signal
        if plot:
            p1 = figure(plot_width=900, plot_height=500, title='Audio Signal', 
                        x_axis_label='Time (s)', y_axis_label='Amplitude (arb. units)')
            time = np.linspace(0, len(channels)/framerate, len(channels))
            p1.line(time[0::1000], channels[0::1000])
            show(p1)
        return channels, framerate
    
    # Record audio file using pyaudio and plot signal
    def record_audiofile(self, plot, filename):
        rec_time = int(input('How long do you want to record? Enter time in seconds: '))
        start_rec = input('Do you want to start recoding? Enter "y" to start:')
        self.songname = filename  
        if start_rec=='y':
            chk_size = 8192  # chunk size
            fmt = pyaudio.paInt16  # format of audio 
            chan = 2  # Number of channels 
            samp_rate = 44100  # sampling rate
            framerate = samp_rate
            p = pyaudio.PyAudio()  # Initializing pyaudio object to open audio stream
            astream = p.open(format=fmt, channels=chan, rate=samp_rate,
                             input=True, frames_per_buffer=chk_size)
            songdata = []
            channels = []
            channels = [[] for i in range(chan)]
            for i in range(0, np.int(samp_rate / chk_size * rec_time)):
                songdata = astream.read(chk_size)
                nums = np.fromstring(songdata, dtype=np.int16)
                for c in range(chan):
                    channels[c].extend(nums[c::chan])
            # Close audio stream
            astream.stop_stream()
            astream.close()
            p.terminate()
        else:
            sys.exit('Audio recording did not start. Start over again.')
        channels = np.sum(channels, axis=0) / len(channels)  # Averaging signal over all channels
        # Plot time signal
        if plot:
            p1 = figure(plot_width=900, plot_height=500, title='Audio Signal', 
                        x_axis_label='Time (s)', y_axis_label='Amplitude (arb. units)')
            time = np.linspace(0, len(channels[0])/framerate, len(channels[0]))
            p1.line(time[0::100], channels[0][0::100])
            show(p1)
        return channels, framerate