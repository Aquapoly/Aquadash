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
import {CdkDrag, CdkDragDrop, CdkDropList, moveItemInArray} from '@angular/cdk/drag-drop';

@Component({
  selector: 'app-status-page',
  standalone: true,
  templateUrl: './status-page.component.html',
  styleUrl: './status-page.component.scss',
  imports: [LineChartComponent, FormsModule, CameraPictureComponent, CdkDrag, CdkDropList],
})
export class StatusPageComponent implements OnInit {
  public sensors: Sensor[] = [];
  public sensorLastMeasurements: [key: number, value: number][] = [];
  public columnCount = STATUS_PAGE_DEFAULTS.COLUMN_COUNT;
  public chartSize: number = STATUS_PAGE_DEFAULTS.CHART_SIZE_INITIAL;
  selectedThresholdsDisplay: ChartThresholdDisplay =
    ChartThresholdDisplay.ColoredBackgroundWithLine;

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

  getSensorTitle(sensor: Sensor): string {
    return this.sensorService.getSensorTitle(sensor);
  }

  getLastMeasurement(sensor: Sensor): string {
    const measurement = this.findSensorMeasurement(sensor.sensor_id);
    return measurement?.toString() ?? STATUS_PAGE_DEFAULTS.NO_DATA_MESSAGE;
  }

  getSensorValidity(sensor: Sensor): string {
    const measurement = this.findSensorMeasurement(sensor.sensor_id);

    if (!measurement) {
      return SENSOR_VALIDITY_CLASSES.NEUTRAL;
    }

    if (this.isCriticalThreshold(measurement, sensor)) {
      return SENSOR_VALIDITY_CLASSES.ERROR;
    }

    if (this.isWarningThreshold(measurement, sensor)) {
      return SENSOR_VALIDITY_CLASSES.WARNING;
    }

    return SENSOR_VALIDITY_CLASSES.SUCCESS;
  }

  updateThresholdDisplay() {
    this.globalSettings.setThresholdDisplay(this.selectedThresholdsDisplay);
  }

  protected drop(event: CdkDragDrop<any>){
    moveItemInArray(this.sensors, event.previousIndex, event.currentIndex);
    this.globalSettings.saveSensorOrder(this.getSensorArray());
  }

  private orderSensors():void{
    const order: string[] = this.globalSettings.getSensorOrder();
    this.sensors.sort( (a,b)=> {
      const indexA = order.indexOf(a.sensor_type);
      const indexB = order.indexOf(b.sensor_type);
    
      const posA = indexA === -1 ? Number.MAX_SAFE_INTEGER : indexA;
      const posB = indexB === -1 ? Number.MAX_SAFE_INTEGER : indexB;
    
      return posA - posB;
    });
  }

  private getSensorArray():string[]{
    let order: string[] = [];
    this.sensors.forEach(x => order.push(x.sensor_type));
    return order;
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

    private async loadData() {
    this.sensors = await this.sensorService.getSensors();
    this.orderSensors();
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
}
