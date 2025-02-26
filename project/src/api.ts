import axios from 'axios';
import { EmailRequest, ApprovalRequest } from './types';

const API_URL = 'http://localhost:8000';

export const processEmail = async (request: EmailRequest) => {
  const response = await axios.post(`${API_URL}/process`, request);
  return response.data;
};

export const approveAction = async (request: ApprovalRequest) => {
  const response = await axios.post(`${API_URL}/approve`, request);
  return response.data;
};