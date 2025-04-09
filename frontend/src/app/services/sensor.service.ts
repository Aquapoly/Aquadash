import { HttpClient } from '@angular/common/http';
import { Injectable, Signal, WritableSignal, signal } from '@angular/core';
import { SERVER_URL } from '@app/environment';
import { Measurement } from '@app/interfaces/measurement';
import { Sensor } from '@app/interfaces/sensor';
import { SensorType } from '@app/interfaces/sensor-type';
import { TimeDelta } from '@app/interfaces/time-delta';
import { Observable, catchError, firstValueFrom, of } from 'rxjs';

@Injectable({
  providedIn: 'any',
})
export class SensorService {
  serverUrl = SERVER_URL;
  prototypeId = 0;

  rangeSelect = [
    { name: 'Dernière heure', value: new TimeDelta(0, 1, 0, 0) },
    { name: 'Dernières 24h', value: new TimeDelta(1, 0, 0, 0) },
    { name: 'Dernière semaine', value: new TimeDelta(7, 0, 0, 0) },
    { name: 'Dernière année', value: new TimeDelta(365, 0, 0, 0) },
  ];
  time_delta: WritableSignal<TimeDelta> = signal(this.rangeSelect[3].value);

  constructor(private httpClient: HttpClient) {}

  timeToPythonString(
    days: number,
    hours: number,
    minutes: number,
    seconds: number
  ): string {
    return `${days.toString().padStart(2, '0')}d,${hours
      .toString()
      .padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds
      .toString()
      .padStart(2, '0')}`;
  }

  getSensorMeasurementsDelta(
    sensor_id: number,
    time_delta: TimeDelta
  ): Promise<Measurement[]> {
    const time_delta_str = time_delta.toString();
    return firstValueFrom(
      this.httpClient.get<Measurement[]>(
        `${this.serverUrl}/measurements/${sensor_id}?time_delta=${time_delta_str}`
      )
    );
  }

  getSensorMeasurements(
    sensor_id: number,
    start_time: string,
    end_time: string
  ): Promise<Measurement[]> {
    return firstValueFrom(
      this.httpClient.get<Measurement[]>(
        `${this.serverUrl}/measurements/${sensor_id}?start_time=${start_time}+end_time=${end_time}`
      )
    );
  }

  getLastMeasurement(sensor_id: number): Promise<Measurement> {
    const observer = this.httpClient
      .get<Measurement>(`${this.serverUrl}/measurements/${sensor_id}/last`)
      .pipe(
        catchError(
          this.handleError<Measurement>(
            `error getting measurement for sensor id ${sensor_id}`
          )
        )
      );
    return firstValueFrom(observer);
  }

  async getSensors(): Promise<Sensor[]> {
    const observer = this.httpClient
      .get<Sensor[]>(`${this.serverUrl}/sensors/${this.prototypeId}`)
      .pipe(
        catchError(
          this.handleError<Sensor[]>(
            `error getting sensors for prototype ${this.prototypeId}`
          )
        )
      );
    return firstValueFrom(observer);
  }

  getSensorTitle(sensor: Sensor) {
    const type = sensor.sensor_type;
    let titleFromType: any = {};
    titleFromType[SensorType.ec] = 'EC';
    titleFromType[SensorType.ph] = 'pH';
    titleFromType[SensorType.temperature] = 'Température';
    titleFromType[SensorType.humidity] = 'Humidité';
    titleFromType[SensorType.water_level] = "Niveau d'eau";
    titleFromType[SensorType.boolean_water_level] = "Niveau d'eau";
    titleFromType[SensorType.oxygen] = 'Oxygène';

    return titleFromType[type];
  }

  private handleError<T>(
    request: string,
    result?: T
  ): (error: Error) => Observable<T> {
    return () => of(result as T);
  }
}
