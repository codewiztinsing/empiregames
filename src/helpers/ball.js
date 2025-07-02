// Generate random number between min and max (inclusive)
const getRandomNumber = (min, max) => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

// Get letter for number
const getLetter = (number) => {
  if (number <= 15) return 'B';
  if (number <= 30) return 'I'; 
  if (number <= 45) return 'N';
  if (number <= 60) return 'G';
  return 'O';
};

// Generate unique random numbers
const generateUniqueNumbers = () => {
  const numbers = new Set();
  while (numbers.size < 75) {
    numbers.add(getRandomNumber(1, 75));
  }
  return Array.from(numbers);
};

// Create ball with letter-number combination
const createBall = (number) => {
  return {
    letter: getLetter(number),
    number: number,
    combined: `${getLetter(number)}${number}`
  };
};

// Generate all balls in random order
export const generateBalls = () => {
  const number = getRandomNumber(1, 75);
  return createBall(number);
  
};


export default generateBalls;