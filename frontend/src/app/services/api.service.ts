import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { SERVER_URL } from '@app/environment';
import { Actuator } from '@app/interfaces/actuator';
import { Notification} from '@app/interfaces/notification';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  serverUrl = SERVER_URL;

  constructor(private http: HttpClient) {}

  getActuators(prototype_id: number) {
    return this.http.get(this.serverUrl + `/actuators/${prototype_id}`, {
      observe: 'response',
    });
  }

  patchActuators(actuators: Actuator[]) {
    return this.http.patch(this.serverUrl + '/actuators', actuators, {
      observe: 'response',
    });
  }
  
  //Notifications
  getNotifications(onlyUnread: boolean = false) {
    const url = onlyUnread
      ? `${this.serverUrl}/notifications?only_unread=true`
      : `${this.serverUrl}/notifications`;
    return this.http.get<Notification[]>(url);
  }

  postNotification(message: string) { //pas tres certain de l'utilité dun post
    return this.http.post<Notification>(`${this.serverUrl}/notifications`, {
      message,
    });
  }

  markNotificationAsRead(id: number) {
    return this.http.patch<Notification>(
      `${this.serverUrl}/notifications/${id}/read`,
      {}
    );
  }

}
