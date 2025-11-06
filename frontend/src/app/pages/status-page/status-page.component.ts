import { Component, OnInit } from '@angular/core';
import { Sensor } from '@app/interfaces/sensor';
import { SensorService } from '@app/services/sensor.service';
import { FormsModule } from '@angular/forms';
import { Measurement } from '@app/interfaces/measurement';
import { CameraPictureComponent } from '@app/components/camera-picture/camera-picture.component';
import {
  CHART_CHOICES,
  ChartThresholdDisplay,
  STATUS_PAGE_DEFAULTS,
  SENSOR_VALIDITY_CLASSES,
} from '@app/constants/constants';
import { GlobalSettingsService } from '@app/services/global-settings.service/global-settings.service';
import { LineChartComponent } from '@app/components/line-chart/line-chart.component';
import { SensorUnitsUtils } from '@app/utils/sensor-units.utils';

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
  public columnCount = STATUS_PAGE_DEFAULTS.COLUMN_COUNT;
  public chartSize: number = STATUS_PAGE_DEFAULTS.CHART_SIZE_INITIAL;
  selectedThresholdsDisplay: ChartThresholdDisplay =
    ChartThresholdDisplay.ColoredBackgroundWithLine;
  private updatingSensors = new Set<number>();

  constructor(
    private readonly sensorService: SensorService,
    private readonly globalSettings: GlobalSettingsService
  ) {}

  get chartChoices(): string[] {
    return Object.values(CHART_CHOICES);
  }
  ngOnInit() {
    this.loadData();
  }

  private async loadData() {
    this.sensors = await this.sensorService.getSensors();

    this.sensors.forEach((sensor) => this.setUnitFromLocalStorage(sensor));

    this.chartSize =
      STATUS_PAGE_DEFAULTS.CHART_SIZE_DIVISOR /
      Math.ceil(this.sensors.length / this.columnCount);
    this.sensorLastMeasurements = await Promise.all(
      this.sensors.map(async (sensor) => {
        const last_measurement: Measurement =
          await this.sensorService.getLastMeasurement(sensor.sensor_id);
        return [sensor.sensor_id, last_measurement?.value];
      })
    );
  }

  private findSensorMeasurement(sensorId: number): number | undefined {
    return this.sensorLastMeasurements.find((msr) => msr[0] === sensorId)?.[1];
  }

  getSensorTitle(sensor: Sensor): string {
    return this.sensorService.getSensorTitle(sensor);
  }

  getLastMeasurement(sensor: Sensor): string {
    const measurement = this.findSensorMeasurement(sensor.sensor_id);
    const displayValue = SensorUnitsUtils.convertUnitToPref(
      sensor,
      measurement
    );
    return displayValue?.toString() ?? STATUS_PAGE_DEFAULTS.NO_DATA_MESSAGE;
  }

  getSensorValidity(sensor: Sensor): string {
    if (this.updatingSensors.has(sensor.sensor_id)) {
      return SENSOR_VALIDITY_CLASSES.NEUTRAL; // ou NEUTRAL, au choix visuel
    }

    const measurement = this.findSensorMeasurement(sensor.sensor_id);

    if (!measurement) {
      return SENSOR_VALIDITY_CLASSES.NEUTRAL;
    }

    const convertedMeasurement = SensorUnitsUtils.convertUnitToPref(
      sensor,
      measurement
    );

    if (this.isCriticalThreshold(convertedMeasurement, sensor)) {
      return SENSOR_VALIDITY_CLASSES.ERROR;
    }

    if (this.isWarningThreshold(convertedMeasurement, sensor)) {
      return SENSOR_VALIDITY_CLASSES.WARNING;
    }

    return SENSOR_VALIDITY_CLASSES.SUCCESS;
  }

  private isCriticalThreshold(measurement: number, sensor: Sensor): boolean {
    return (
      measurement < sensor.threshold_critically_low ||
      measurement > sensor.threshold_critically_high
    );
  }

  private isWarningThreshold(measurement: number, sensor: Sensor): boolean {
    return (
      measurement < sensor.threshold_low || measurement > sensor.threshold_high
    );
  }

  updateThresholdDisplay() {
    this.globalSettings.setThresholdDisplay(this.selectedThresholdsDisplay);
  }

  getAvailableUnits(sensor: Sensor): string[] {
    return SensorUnitsUtils.getUnits(sensor.sensor_type);
  }

  private setUnitFromLocalStorage(sensor: Sensor) {
    const savedUnit = this.globalSettings.getSensorUnit(sensor.sensor_type);
    sensor.sensor_unit =
      savedUnit || SensorUnitsUtils.getDefaultUnit(sensor.sensor_type) || '';
  }

  onUnitChange(sensor: Sensor): void {
    this.updatingSensors.add(sensor.sensor_id);

    this.globalSettings.setSensorUnit(sensor.sensor_type, sensor.sensor_unit);
    setTimeout(() => this.updatingSensors.delete(sensor.sensor_id), 10);
  }

  onSensorUpdated(updatedSensor: Sensor): void {
    const index = this.sensors.findIndex(
      (s) => s.sensor_id === updatedSensor.sensor_id
    );
    if (index !== -1) {
      this.sensors[index] = { ...updatedSensor };
    }
  }
}
