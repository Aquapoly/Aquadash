import { Component, Input, OnInit } from '@angular/core';
import { Sensor } from '@app/interfaces/sensor';
import { WHOLE_GAUGE_ROTATION_OFFSET } from '@app/constants/constants';

@Component({
  selector: 'app-gauge-chart',
  imports: [],
  templateUrl: './gauge-chart.component.html',
  styleUrl: './gauge-chart.component.scss',
})
export class GaugeChartComponent implements OnInit {
  @Input() sensor: Sensor = {} as Sensor;
  gaugeAngles: string[] = [];
  minValue: number = 0;
  maxValue: number = 14;
  currentValue: number = 7.1;
  gaugeCurrentColor: string = '';

  constructor() {}

  ngOnInit(): void {
    // TODO: min/max values and ranges will be fetched from server/parent node as input, and unit
    // depends on sensor configuration
    const errorRange = [4.5, 7.5];
    const warningRange = [5.5, 6.5];

    this.gaugeAngles = [
      this.computeGaugeAngle(
        errorRange[0],
        this.minValue,
        this.maxValue
      ).toString(),
      this.computeGaugeAngle(
        warningRange[0],
        this.minValue,
        this.maxValue
      ).toString(),
      this.computeGaugeAngle(
        warningRange[1],
        this.minValue,
        this.maxValue
      ).toString(),
      this.computeGaugeAngle(
        errorRange[1],
        this.minValue,
        this.maxValue
      ).toString(),
    ];

    this.setGaugeColor(errorRange, warningRange);
  }

  setGaugeColor(errorRange: number[], warningRange: number[]) {
    if (
      this.currentValue <= errorRange[0] ||
      this.currentValue >= errorRange[1]
    ) {
      this.gaugeCurrentColor = 'to-error';
    } else if (
      this.currentValue <= warningRange[0] ||
      this.currentValue >= warningRange[1]
    ) {
      this.gaugeCurrentColor = 'to-warning';
    } else {
      this.gaugeCurrentColor = 'to-success';
    }
  }

  computeGaugeAngle(value: number, min: number, max: number): number {
    const fillPercentage = this.clamp((value - min) / (max - min), 0, 1);
    const angle = Math.round(fillPercentage * 180);
    return angle - WHOLE_GAUGE_ROTATION_OFFSET;
  }

  getCurrentGaugeAngle() {
    return this.computeGaugeAngle(
      this.currentValue,
      this.minValue,
      this.maxValue
    );
  }

  clamp(val: number, min: number, max: number) {
    return Math.min(Math.max(val, min), max);
  }
}
