import axios from 'axios';

const API_BASE_URL = '/accounts';

// Service for login logs
export const loginLogService = {
  // Get login logs
  getLoginLogs: async (limit = 50, offset = 0) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/login-logs/?limit=${limit}&offset=${offset}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Failed to fetch login logs' };
    }
  },
};