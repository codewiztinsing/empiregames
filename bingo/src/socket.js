import { io } from 'socket.io-client';

const URL = process.env.REACT_APP_SOCKET_URL;
// const URL = "http://server.wowliyubingo.com";
const socket = io(URL, {
  autoConnect: false, // we'll manually connect to control timing
  transports: ['websocket'],
});

export default socket;
