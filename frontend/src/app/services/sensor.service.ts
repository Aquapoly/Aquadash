import { HttpClient } from '@angular/common/http';
import { Injectable, Signal, WritableSignal, signal } from '@angular/core';
import { SERVER_URL } from '@app/environment';
import { Measurement } from '@app/interfaces/measurement';
import { Sensor } from '@app/interfaces/sensor';
import { SensorType } from '@app/interfaces/sensor-type';
import { TimeDelta } from '@app/interfaces/time-delta';
import { Observable, catchError, firstValueFrom, of } from 'rxjs';
import {
  SENSOR_SERVICE_DEFAULTS,
  TIME_RANGE_OPTIONS,
  SENSOR_TYPE_TITLES,
  API_ENDPOINTS,
} from '@app/constants/constants';

@Injectable({
  providedIn: 'any',
})
export class SensorService {
  private readonly serverUrl = SERVER_URL;
  private readonly prototypeId = SENSOR_SERVICE_DEFAULTS.PROTOTYPE_ID;

  readonly rangeSelect = this.createTimeRangeOptions();
  time_delta: WritableSignal<TimeDelta> = signal(
    this.rangeSelect[SENSOR_SERVICE_DEFAULTS.DEFAULT_RANGE_INDEX].value
  );

  constructor(private readonly httpClient: HttpClient) {}

  private createTimeRangeOptions() {
    return TIME_RANGE_OPTIONS.map((option) => ({
      name: option.name,
      value: new TimeDelta(
        option.value.days,
        option.value.hours,
        option.value.minutes,
        option.value.seconds
      ),
    }));
  }

  private padNumber(num: number): string {
    const { PADDING_LENGTH, PADDING_CHAR } = SENSOR_SERVICE_DEFAULTS;
    return num.toString().padStart(PADDING_LENGTH, PADDING_CHAR);
  }

  timeToPythonString(
    days: number,
    hours: number,
    minutes: number,
    seconds: number
  ): string {
    return `${this.padNumber(days)}d,${this.padNumber(hours)}:${this.padNumber(
      minutes
    )}:${this.padNumber(seconds)}`;
  }

  private buildMeasurementsUrl(sensorId: number, queryParams: string): string {
    return `${this.serverUrl}/${API_ENDPOINTS.MEASUREMENTS}/${sensorId}${queryParams}`;
  }

  getSensorMeasurementsDelta(
    sensor_id: number,
    time_delta: TimeDelta
  ): Promise<Measurement[]> {
    const url = this.buildMeasurementsUrl(
      sensor_id,
      `?time_delta=${time_delta.toString()}`
    );
    return firstValueFrom(this.httpClient.get<Measurement[]>(url));
  }

  getSensorMeasurements(
    sensor_id: number,
    start_time: string,
    end_time: string
  ): Promise<Measurement[]> {
    const url = this.buildMeasurementsUrl(
      sensor_id,
      `?start_time=${start_time}+end_time=${end_time}`
    );
    return firstValueFrom(this.httpClient.get<Measurement[]>(url));
  }

  getLastMeasurement(sensor_id: number): Promise<Measurement> {
    const url = this.buildMeasurementsUrl(sensor_id, `/${API_ENDPOINTS.LAST}`);
    return firstValueFrom(
      this.httpClient
        .get<Measurement>(url)
        .pipe(
          catchError(
            this.handleError<Measurement>(
              `error getting measurement for sensor id ${sensor_id}`
            )
          )
        )
    );
  }

  async getSensors(): Promise<Sensor[]> {
    const url = `${this.serverUrl}/${API_ENDPOINTS.SENSORS}/${this.prototypeId}`;
    return firstValueFrom(
      this.httpClient
        .get<Sensor[]>(url)
        .pipe(
          catchError(
            this.handleError<Sensor[]>(
              `error getting sensors for prototype ${this.prototypeId}`
            )
          )
        )
    );
  }

  getSensorTitle(sensor: Sensor): string {
    return SENSOR_TYPE_TITLES[sensor.sensor_type];
  }

  private handleError<T>(
    request: string,
    result?: T
  ): (error: Error) => Observable<T> {
    return () => of(result as T);
  }
}
