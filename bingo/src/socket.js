import { io } from 'socket.io-client';

const URL = process.env.REACT_APP_SOCKET_URL;
console.log("URL - ",URL)

const socket = io(URL, {
  autoConnect: false, // we'll manually connect to control timing
  transports: ['websocket'],
});

export default socket;
