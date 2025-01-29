import axios from 'axios';
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL;

const service = axios.create({
  baseURL: API_BASE_URL,
});

service.interceptors.request.use((config) => {
  return config;
}, (error) => {
  return Promise.reject(error);
});

service.interceptors.response.use((response) => {
  return response;
}, (error) => {
  // return Promise.reject(error);
});

export default service;
