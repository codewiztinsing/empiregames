import { io } from 'socket.io-client';

// Use wss:// for secure WebSocket connection
const URL = "wss://server.wowliyubingo.com";
// const URL = "http://server.wowliyubingo.com";
const socket = io(URL, {
  autoConnect: false, // we'll manually connect to control timing
  transports: ['websocket'],
});

export default socket;
