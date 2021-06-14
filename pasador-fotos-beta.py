#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This is a small example which creates a twitch stream to connect with
and changes the color of the video according to the colors provided in
the chat.
"""
from __future__ import print_function
from twitchstream.outputvideo import TwitchBufferedOutputStream
from twitchstream.chat import TwitchChatStream
import argparse
import time
import numpy as np
from matplotlib import image
from PIL import Image


if __name__ == "__main__":
    def update(t):
        photo = Image.open('img/image'+str(t)+'.jpg')
        photo = photo.resize((640, 480), Image.ANTIALIAS)
        #photo =photo.convert("RGB")
        return np.asarray(photo).copy()

        
    parser = argparse.ArgumentParser(description=__doc__)
    required = parser.add_argument_group('required arguments')
    required.add_argument('-u', '--username',
                          help='twitch username',
                          required=True)
    required.add_argument('-o', '--oauth',
                          help='twitch oauth '
                               '(visit https://twitchapps.com/tmi/ '
                               'to create one for your account)',
                          required=True)
    required.add_argument('-s', '--streamkey',
                          help='twitch streamkey',
                          required=True)
    args = parser.parse_args()
    
    # load two streams:
    # * one stream to send the video
    f=1
    foto=update(f)

    #photo = Image.open('img/image'+n+'.jpg')
    #photo = photo.resize((640, 480), Image.ANTIALIAS)
    #photo =photo.convert("RGB")

    #foto = np.asarray(photo).copy()
    #foto[:,:,0]=np.asarray(photo)[:,:,0]
    #foto[:,:,1]=np.asarray(photo)[:,:,1]
    #foto[:,:,2]=np.asarray(photo)[:,:,2]

    with TwitchBufferedOutputStream(
            twitch_stream_key=args.streamkey,
            width=640,
            height=480,
            fps=30.,
            enable_audio=True,
            verbose=False) as videostream:#, \
        #TwitchChatStream(
        #    username=args.username,
        #    oauth=args.oauth,
        #    verbose=False) as chatstream:

        # Send a chat message to let everybody know you've arrived
       # chatstream.send_chat_message("Taking requests!")

        frame = np.zeros((480, 640, 3))
        frequency = 100
        last_phase = 0

        # The main loop to create videos
        n=0
        while True:

            
            if videostream.get_video_frame_buffer_state() < 30:
                videostream.send_video_frame(np.array(foto))
               
                if n%600==0:
                    f=f+1
                    foto=update(f)
                else:
                    a=1
                n=n+1

            # If there are not enough audio fragments left,
            # add some more, but take care to stay in sync with
            # the video! Audio and video buffer separately,
            # so they will go out of sync if the number of video
            # frames does not match the number of audio samples!
            elif videostream.get_audio_buffer_state() < 30:
                x = np.linspace(last_phase,
                                last_phase +
                                frequency*2*np.pi/videostream.fps,
                                int(44100 / videostream.fps) + 1)
                last_phase = x[-1]
                audio = np.sin(x[:-1])
                #videostream.send_audio(audio, audio)

            # If nothing is happening, it is okay to sleep for a while
            # and take some pressure of the CPU. But not too long, if
            # the buffers run dry, audio and video will go out of sync.
            else:
                time.sleep(.001)