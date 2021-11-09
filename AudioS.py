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
        self.framerate = []
        self.original_sound = self.read_audiofile()
        self.original_signal = self.get_audiosignal(self.original_sound)
        
    def read_audiofile(self):
        print('----------------------')
        name = input('Enter the audio filename you want to read including the extension: ')
        print('----------------------')
        filename, file_ext = os.path.splitext(name)
        filename = os.getcwd() + '/samples/' + name
        audiofile = pydub.AudioSegment.from_file(filename, file_ext)
        self.framerate = audiofile.frame_rate
        return audiofile
    
    def get_audiosignal(self, aseg):
        songdata = []  # Empty list for holding audio data
        channels = []  # Empty list to hold data from separate channels
        songdata = np.frombuffer(aseg._data, np.int16)
        for chn in range(aseg.channels):
            channels.append(songdata[chn::aseg.channels])  # separate signal from channels
        signal = np.sum(channels, axis=0) / len(channels)  # Averaging signal over all channels
        signal = self.norm_signal(signal)  # normalize signal amplitude
        return signal
        
    def norm_signal(self, input_signal):
        output_signal = input_signal / np.max(np.absolute(input_signal))
        return output_signal
        
    def plot_signal(self, aseg):
        asig = self.get_audiosignal(aseg)
        framerate = aseg.frame_rate
        p = figure(plot_width=900, plot_height=500, title='Audio Signal', 
                   x_axis_label='Time (s)', y_axis_label='Amplitude (arb. units)')
        time = np.linspace(0, len(asig) / framerate, len(asig))
        m = int(len(asig) / 2000)
        p.line(time[0::m], asig[0::m], line_color=Colorblind[8][0], alpha=0.6)
        show(p)
        
    def scratch_params(self, M=5, T=1000, N=1):
        print('----------------------')
        scpflag = input('Do you want to manually enter scratching parameters (y/n): ')
        print('----------------------')
        if (scpflag == 'y'):
            M = float(input('Enter the max speed-up in a scratch (number between 1 and 10): '))
            T = int(input('Enter the duration of a scratch in milisecs (> 200 ms): '))
            N = int(input('Enter the number of scratches (number between 1 and 2): '))
            print('----------------------')
        return M, T, N
        
        
    # def change_playrate(self, prate=4.5):
    #     audiofile = self.sound.speedup(prate)
    #     songdata = []  # Empty list for holding audio data
    #     channels = []  # Empty list to hold data from separate channels
    #     songdata = np.frombuffer(audiofile._data, np.int16)
    #     for chn in range(audiofile.channels):
    #         channels.append(songdata[chn::audiofile.channels])  # separate signal from channels
    #     self.signal = np.sum(channels, axis=0) / len(channels)  # Averaging signal over all channels
    #     self.signal = self.norm_signal(self.signal)  # normalize signal amplitude
    #     self.plot_signal([self.signal], True)    
        
    def scratch_audiofile(self, aseg):
        mult, tscr, nums = self.scratch_params()
        tin = 2000  
        s_before = aseg[: tin]
        s_scr = aseg[tin : tin + tscr]
        s_after = aseg[tin + tscr :]
        s_scr = s_scr.speedup(playback_speed=mult)
        s_scr2 = s_scr.reverse()
        s_scr = s_scr.append(s_scr2, crossfade=25)
        for n in range(nums):
            s_before = s_before.append(s_scr, crossfade=25)
        s_new = s_before.append(s_after, crossfade=25)
        self.scratched_sound = s_new
        self.scratched_signal = self.get_audiosignal(s_new)
        self.plot_signal(s_new)



        
        
        