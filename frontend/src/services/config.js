const config = {
    API_URL: process.env.REACT_APP_API_URL ? `${process.env.REACT_APP_API_URL}/api` : 'http://localhost:8000/api'
};

console.log('Environment:', process.env.NODE_ENV);
console.log('API URL:', config.API_URL);
console.log('Raw REACT_APP_API_URL:', process.env.REACT_APP_API_URL);

export default config; 