import React from 'react';
import Sound from 'react-sound';

const PlaySound = () => {
  return (
    <Sound
      url="cool_sound.mp3"
      playStatus={Sound.status.PLAYING}
      playFromPosition={300 /* in milliseconds */}
      onLoading={this.handleSongLoading}
      onPlaying={this.handleSongPlaying}
      onFinishedPlaying={this.handleSongFinishedPlaying}
    />
  );
};  



export default PlaySound;