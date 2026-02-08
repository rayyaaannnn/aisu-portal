// services/notificationService.js

class NotificationService {
  constructor() {
    this.baseUrl = '/accounts';
  }

  async getNotifications() {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch(`${this.baseUrl}/notifications/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching notifications:', error);
      return { notifications: [], unread_count: 0 };
    }
  }

  async markAsRead(notificationId) {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch(`${this.baseUrl}/notifications/${notificationId}/mark-read/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error marking notification as read:', error);
      return { success: false };
    }
  }

  async markAllAsRead() {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch(`${this.baseUrl}/notifications/mark-all-read/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      return { success: false };
    }
  }
}

export default new NotificationService();