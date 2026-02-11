import axios from 'axios';

const api = axios.create({
  baseURL: '/api',  // This will be proxied to http://localhost:8000/api
  withCredentials: true,
});

// Optional: Add request interceptor for debugging
api.interceptors.request.use(
  config => {
    console.log('API Request:', config.method.toUpperCase(), config.url);
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Optional: Add response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default api;