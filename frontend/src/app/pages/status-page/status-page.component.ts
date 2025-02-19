import { Component, OnInit } from '@angular/core';
import { LineChartComponent } from '@app/components/line-chart/line-chart.component';
import { Sensor } from '@app/interfaces/sensor';
import { SensorService } from '@app/services/sensor.service';
import { GaugeChartComponent } from '@app/components/gauge-chart/gauge-chart.component';
import { FormsModule } from '@angular/forms';
import { TimeDelta } from '@app/interfaces/time-delta';
import { Measurement } from '@app/interfaces/measurement';

@Component({
  selector: 'app-status-page',
  standalone: true,
  templateUrl: './status-page.component.html',
  styleUrl: './status-page.component.scss',
  imports: [LineChartComponent, GaugeChartComponent, FormsModule],
})
export class StatusPageComponent implements OnInit {
  public sensors: Sensor[] = [];
  public sensorLastMeasurements: [key: number, value: number][] = [];
  public columnCount = 2;
  public chartSize: number = 100;
  selectedRange: TimeDelta = this.rangeSelect[0].value;

  constructor(private sensorService: SensorService) {}

  get rangeSelect() {
    return this.sensorService.rangeSelect;
  }

  async ngOnInit() {
    this.sensors = await this.sensorService.getSensors();
    // if(this.sensors.length < 2) this.columnCount = '1'; //Yep we have a little hard-coded
    this.chartSize = 78 / Math.ceil(this.sensors.length / this.columnCount);
    this.sensorLastMeasurements = await Promise.all(
      this.sensors.map(async (sensor) => {
        const last_measurement: Measurement =
          await this.sensorService.getLastMeasurement(sensor.sensor_id);
        return [sensor.sensor_id, last_measurement?.value];
      })
    );
  }

  getSensorTitle(sensor: Sensor): string {
    return this.sensorService.getSensorTitle(sensor);
  }

  getLastMeasurement(sensor: Sensor): string {
    const last_measurement = this.sensorLastMeasurements.find(
      (msr) => msr[0] === sensor.sensor_id
    );
    // Display no data if sensor has no measurements instead of undefined
    return last_measurement && last_measurement[1]
      ? last_measurement[1]?.toString()
      : 'No data';
  }

  getSensorValidity(sensor: Sensor): string {
    const get_measurement = this.sensorLastMeasurements.find(
      (msr) => msr[0] === sensor.sensor_id
    );
    if (!get_measurement || !get_measurement[1]) {
      return 'neutral-content';
    }

    const last_measurement = get_measurement[1];

    const validity: string =
      last_measurement < sensor.threshold_critically_low ||
      last_measurement > sensor.threshold_critically_high
        ? 'error'
        : last_measurement < sensor.threshold_low ||
          last_measurement > sensor.threshold_high
        ? 'warning'
        : 'success';

    return validity;
  }

  async setDelta() {
    console.log(this.selectedRange);
    this.sensorService.time_delta.set(this.selectedRange);
    // Update last measurement in case it changed
    this.sensorLastMeasurements = await Promise.all(
      this.sensors.map(async (sensor) => {
        const last_measurement: Measurement =
          await this.sensorService.getLastMeasurement(sensor.sensor_id);
        return [sensor.sensor_id, last_measurement?.value];
      })
    );
  }
}
