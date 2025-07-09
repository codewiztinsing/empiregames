import { io } from 'socket.io-client';

// const URL = process.env.SERVER_URL; // Change to your backend URL
const URL = "http://localhost:5000";
console.log("URL", URL);
const socket = io(URL, {
  autoConnect: false, // we'll manually connect to control timing
  transports: ['websocket'],
});

export default socket;
