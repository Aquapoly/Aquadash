import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Notification, mockNotifications } from '@app/interfaces/notification';

@Component({
  selector: 'app-notifications',
  imports: [CommonModule],
  templateUrl: './notifications.component.html',
  styleUrl: './notifications.component.scss',
})
export class NotificationsComponent {
  notifications: Notification[] = mockNotifications;

  protected deleteNotification(notificationId: number) {
    this.markAsRead(notificationId);
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
    return this.notifications.filter((n) => !n.read).length;
  }

  get unreadNotifications(): Notification[] {
    return this.notifications.filter((n) => !n.read);
  }
}
