import { Component, OnInit } from '@angular/core';
import { Sensor } from '@app/interfaces/sensor';
import { SensorService } from '@app/services/sensor.service';
import { FormsModule } from '@angular/forms';
import { Measurement } from '@app/interfaces/measurement';
import { CameraPictureComponent } from '@app/components/camera-picture/camera-picture.component';
import {
  CHART_CHOICES,
  ChartThresholdDisplay,
} from '../../../constants/constants';
import { GlobalSettingsService } from '@app/services/global-settings.service/global-settings.service';
import { LineChartComponent } from '@app/components/line-chart/line-chart.component';

@Component({
  selector: 'app-status-page',
  standalone: true,
  templateUrl: './status-page.component.html',
  styleUrl: './status-page.component.scss',
  imports: [LineChartComponent, FormsModule, CameraPictureComponent],
})
export class StatusPageComponent implements OnInit {
  public sensors: Sensor[] = [];
  public sensorLastMeasurements: [key: number, value: number][] = [];
  public columnCount = 2;
  public chartSize: number = 100;
  selectedThresholdsDisplay: ChartThresholdDisplay =
    ChartThresholdDisplay.ColoredBackgroundWithLine;

  constructor(
    private sensorService: SensorService,
    private globalSettings: GlobalSettingsService
  ) {}

  get chartChoices(): string[] {
    return Object.values(CHART_CHOICES);
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

  updateThresholdDisplay() {
    this.globalSettings.setThresholdDisplay(this.selectedThresholdsDisplay);
  }
}
