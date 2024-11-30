import { Component, Input, OnInit } from '@angular/core';
import { Sensor } from '@app/interfaces/sensor';
import { SensorService } from '@app/services/sensor.service';

@Component({
  selector: 'app-gauge-chart',
  standalone: true,
  imports: [],
  templateUrl: './gauge-chart.component.html',
  styleUrl: './gauge-chart.component.css'
})
export class GaugeChartComponent implements OnInit {
  @Input() sensor: Sensor = {} as Sensor;
  // Necessary because the whole gauge is rotated 45 degrees, 
  // for the rounded corner to be on top, giving the circular look in CSS:
  WHOLE_GAUGE_ROTATION_OFFSET: number = 45; 
  
  gaugeAngles: string[] = [];
  minValue: number = 0;
  maxValue: number = 14;
  currentValue: number = 7.1;
  gaugeCurrentColor: string = "";

  constructor(private sensorService: SensorService) {}
  
  ngOnInit(): void {
    // TODO: min/max values and ranges will be fetched from server/parent node as input, and unit
    // depends on sensor configuration
    const errorRange = [4.5, 7.5];
    const warningRange = [5.5, 6.5];

    this.gaugeAngles = [
      this.computeGaugeAngle(errorRange[0], this.minValue, this.maxValue).toString(),
      this.computeGaugeAngle(warningRange[0], this.minValue, this.maxValue).toString(),
      this.computeGaugeAngle(warningRange[1], this.minValue, this.maxValue).toString(),
      this.computeGaugeAngle(errorRange[1], this.minValue, this.maxValue).toString(),
    ];
    // const values = this.sensorService.getSensorMeasurementsDelta(this.sensor.sensor_type, '');
    // this.currentValue = values[values.length - 1].value;

    this.setGaugeColor(errorRange, warningRange);
  }

  setGaugeColor(errorRange: number[], warningRange: number[]) {
    if(this.currentValue <= errorRange[0] || this.currentValue >= errorRange[1]) {
      this.gaugeCurrentColor = "to-error";
    }
    else if(this.currentValue <= warningRange[0] || this.currentValue >= warningRange[1]) {
      this.gaugeCurrentColor = "to-warning";
    }
    else {
      this.gaugeCurrentColor = "to-success";
    }
  }

  computeGaugeAngle(value: number, min: number, max: number): number {
    const fillPercentage = this.clamp((value - min) / (max-min), 0, 1);
    const angle = Math.round(fillPercentage * 180);
    return angle - this.WHOLE_GAUGE_ROTATION_OFFSET;
  }

  getCurrentGaugeAngle() {
    return this.computeGaugeAngle(this.currentValue, this.minValue, this.maxValue);
  }

  clamp(val: number, min: number, max: number) {
    return Math.min(Math.max(val, min), max);
  }
}
