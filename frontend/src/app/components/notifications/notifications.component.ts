import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import {
  Notification,
  NotificationType,
  mockNotifications,
} from '@app/interfaces/notification';

@Component({
  selector: 'app-notifications',
  imports: [CommonModule],
  templateUrl: './notifications.component.html',
  styleUrl: './notifications.component.scss',
})
export class NotificationsComponent {
  notifications: Notification[] = mockNotifications;

  protected dismissNotification(notificationId: number) {
    const notification = this.notifications.find(
      (n) => n.id === notificationId
    );
    if (notification) notification.dismissed = true;
  }

  protected toggleNotificationsMenu() {
    this.notifications.forEach((n) => {
      n.read = true;
    });
  }

  protected markAsRead(notificationId: number) {
    const notification = this.notifications.find(
      (n) => n.id === notificationId
    );
    if (notification) notification.read = true;
  }

  get unreadCount(): number {
    return this.notifications.filter((n) => !n.read && !n.dismissed).length;
  }

  get visibleNotifications(): Notification[] {
    return this.notifications.filter((n) => !n.dismissed);
  }

  protected viewAllNotifications() {
    console.log('TODO : rediriger vers la page de notifications');
  }

  getNotificationIcon(notification: Notification): {
    icon: string;
    classes: string;
  } {
    switch (notification.level) {
      case NotificationType.Success:
        return {
          icon: 'M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5Zm3.707 8.207-4 4a1 1 0 0 1-1.414 0l-2-2a1 1 0 0 1 1.414-1.414L9 10.586l3.293-3.293a1 1 0 0 1 1.414 1.414Z',
          classes:
            'text-green-500 bg-green-500 dark:bg-green-800 dark:text-green-200',
        };
      case NotificationType.Warning:
        return {
          icon: 'M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM10 15a1 1 0 1 1 0-2 1 1 0 0 1 0 2Zm1-4a1 1 0 0 1-2 0V6a1 1 0 0 1 2 0v5Z',
          classes:
            'text-orange-500 bg-orange-500 dark:bg-orange-700 dark:text-orange-200',
        };
      case NotificationType.Error:
        return {
          icon: 'M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5Zm3.707 11.793a1 1 0 1 1-1.414 1.414L10 11.414l-2.293 2.293a1 1 0 0 1-1.414-1.414L8.586 10 6.293 7.707a1 1 0 0 1 1.414-1.414L10 8.586l2.293-2.293a1 1 0 0 1 1.414 1.414L11.414 10l2.293 2.293Z',
          classes: 'text-red-500 bg-red-500 dark:bg-red-800 dark:text-red-200',
        };
      case NotificationType.Info:
      default:
        return {
          icon: 'M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0 2Z',
          classes:
            'text-blue-500 bg-blue-500 dark:bg-blue-800 dark:text-blue-200',
        };
    }
  }
}
