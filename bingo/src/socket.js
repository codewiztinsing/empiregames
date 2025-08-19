import { io } from 'socket.io-client';

const URL = "http://localhost:5000";
// const URL = process.env.REACT_APP_SOCKET_URL;
const socket = io(URL, {
  autoConnect: false, // we'll manually connect to control timing
  transports: ['websocket'],
});

export default socket;
