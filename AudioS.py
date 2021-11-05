import numpy as np
from bokeh.plotting import figure, show
# from bokeh.io import output_notebook
from bokeh.palettes import Colorblind
import pydub
import pyaudio
import os

# This class defines the core Guitar Effects object. 
# It contains functions to read and write audio files.
# It also contains all the different functions implementing various guitar effects

class AudioS():
    
    def __init__(self):
        self.effectname = ''
        self.audiofilename = ''
        self.framerate = []
        self.signal = []
        self.sound = self.read_audiofile()
        
    def read_audiofile(self):
        print('----------------------')
        name = input('Enter the audio filename you want to read including the extension: ')
        print('----------------------')
        filename, file_ext = os.path.splitext(name)
        filename = os.getcwd() + '/samples/' + name
        self.audiofilename = filename
        audiofile = pydub.AudioSegment.from_file(filename, file_ext)
        # audiofile = audiofile.fade_out(2000)
        # audiofile = audiofile.speedup(4.5)
        self.framerate = audiofile.frame_rate
        songdata = []  # Empty list for holding audio data
        channels = []  # Empty list to hold data from separate channels
        songdata = np.frombuffer(audiofile._data, np.int16)
        for chn in range(audiofile.channels):
            channels.append(songdata[chn::audiofile.channels])  # separate signal from channels
        self.signal = np.sum(channels, axis=0) / len(channels)  # Averaging signal over all channels
        self.signal = self.norm_signal(self.signal)  # normalize signal amplitude
        self.plot_signal([self.signal], True)
        return audiofile
        
    def norm_signal(self, input_signal):
        output_signal = input_signal / np.max(np.absolute(input_signal))
        return output_signal
        
    def plot_signal(self, audio_signal, pflag):
        if pflag:
            p = figure(plot_width=900, plot_height=500, title='Audio Signal', 
                       x_axis_label='Time (s)', y_axis_label='Amplitude (arb. units)')
            time = np.linspace(0, np.shape(audio_signal)[1] / self.framerate, np.shape(audio_signal)[1])
            m = int(np.shape(audio_signal)[1] / 2000)
            for n in range(np.shape(audio_signal)[0]):
                labels = 'signal ' + str(n + 1)
                p.line(time[0::m], audio_signal[n][0::m], line_color=Colorblind[8][n], 
                       alpha=0.6, legend_label=labels)
            show(p)
        else:
            pass
        
    def change_playrate(self, prate=4.5):
        audiofile = self.sound.speedup(prate)
        songdata = []  # Empty list for holding audio data
        channels = []  # Empty list to hold data from separate channels
        songdata = np.frombuffer(audiofile._data, np.int16)
        for chn in range(audiofile.channels):
            channels.append(songdata[chn::audiofile.channels])  # separate signal from channels
        self.signal = np.sum(channels, axis=0) / len(channels)  # Averaging signal over all channels
        self.signal = self.norm_signal(self.signal)  # normalize signal amplitude
        self.plot_signal([self.signal], True)
        