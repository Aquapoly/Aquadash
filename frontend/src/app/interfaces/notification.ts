export enum NotificationType {
  Info = 'info',
  Warning = 'warning',
  Error = 'error',
  Success = 'success',
}

export interface Notification {
  id: number;
  timestamp: Date;
  level: NotificationType;
  description: string;
  read?: boolean;
}

export const mockNotifications: Notification[] = [
  {
    id: 1,
    timestamp: new Date(),
    level: NotificationType.Info,
    description: 'System maintenance scheduled for tonight at 11 PM.',
    read: false,
  },
  {
    id: 2,
    timestamp: new Date(),
    level: NotificationType.Warning,
    description: 'The temperature for the Prototype is too high.',
    read: false,
  },
  {
    id: 3,
    timestamp: new Date(),
    level: NotificationType.Error,
    description: 'Failed to connect to the server. Please try again later.',
    read: false,
  },
  {
    id: 4,
    timestamp: new Date(),
    level: NotificationType.Success,
    description: 'Your actuator has been updated successfully.',
    read: false,
  },
];
