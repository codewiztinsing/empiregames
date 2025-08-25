import { io } from 'socket.io-client';

// const URL = process.env.REACT_APP_SERVER_URL;
const URL = "http://localhost:5000";

const socket = io(URL, {
  autoConnect: false, // we'll manually connect to control timing
  transports: ['websocket'],
});

export default socket;
