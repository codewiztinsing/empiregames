import { io } from 'socket.io-client';

const URL = 'http://localhost:5000'; // Change to your backend URL
const socket = io(URL, {
  autoConnect: false, // we'll manually connect to control timing
  transports: ['websocket'],
});

export default socket;
