import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { SERVER_URL } from '@app/environment';
import { Actuator } from '@app/interfaces/actuator';
import { Observable } from 'rxjs';

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

  patchActuator(actuatorId: number, changes: Partial<Actuator>) {
    return this.http.patch(this.serverUrl + `/actuators/${actuatorId}`, changes, {
      observe: 'response',
    });
  }

  exportMeasurements() {
    return this.http.get(this.serverUrl + '/measurements/export', {
      responseType: 'blob',
      observe: 'response',
    });
  }

  postActuator(actuator: Actuator) {
    return this.http.post(this.serverUrl + '/actuators', actuator, {
      observe: 'response',
    });
  }
}
