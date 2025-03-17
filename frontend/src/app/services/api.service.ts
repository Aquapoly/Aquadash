import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { SERVER_URL } from '@app/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  serverUrl = SERVER_URL;

  constructor(private http:HttpClient) { }

  getActuators(prototype_id: number) {
    return this.http.get(this.serverUrl + `/actuators/${prototype_id}`, {observe: 'response'});
  }

  patchActuators(actuators: any) {
    return this.http.patch(this.serverUrl + '/actuators', actuators, {observe: 'response'});
  }

}
