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
        
    def scratch_params(self, M=5, N=1):
        print('----------------------')
        scpflag = input('Do you want to manually enter scratching parameters (y/n): ')
        print('----------------------')
        if (scpflag == 'y'):
            M = float(input('Enter the max speed-up in a scratch (number between 1 and 10): '))
            T = float(input('Enter where you want to insert the scratch (ms): '))
            N = int(input('Enter the number of scratches (number between 1 and 2): '))
            print('----------------------')
        return M, T, N        
        
    def scratch_audiofile(self, aseg):
        mult, tin, nums = self.scratch_params()
        # converting playrate multiplier to duration of scratching
        # assuming pi/2 rotation for a scratch and 1x = 33rpm
        # also converting seconds to miliseconds
        tscr = np.floor(500 / mult)  
        s_before = aseg[: tin]
        s_scr_o = aseg[tin : tin + tscr]
        s_after = aseg[tin + tscr :]
        s_scr_f = s_scr_o.speedup(playback_speed=mult, chunk_size=50, crossfade=25)
        s_scr_r = s_scr_o.reverse()
        s_scr_m = s_scr_f.append(s_scr_r, crossfade=25)
        for n in range(nums-1):
            s_scr_m = s_scr_m.append(s_scr_m, crossfade=25)
        s_new = s_before.append(s_scr_m, crossfade=25)
        s_new = s_new.append(s_after, crossfade=25)
        self.scratched_sound = s_new
        self.scratched_signal = self.get_audiosignal(s_new)
        self.plot_signal(s_new)
        
    def calc_fft(self, asig):
        N = int(len(asig))
        asig_fft = 2.0 / N * np.fft.rfft([asig])
        apower = np.abs(asig_fft)**2
        freqs = np.fft.rfftfreq(n=N, d=1.0/self.framerate)
        p = figure(plot_width=900, plot_height=500, title='Audio Spectrum', 
                   x_axis_label='Frequency (1/s)', y_axis_label='Amplitude (arb. units)')
        p.line(freqs, np.log10(apower[0, :]), line_color=Colorblind[8][0], alpha=0.6)
        show(p)


        
        
        