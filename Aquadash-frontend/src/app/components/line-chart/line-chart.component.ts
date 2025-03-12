import { AfterViewInit, Component, Input, OnInit, effect } from '@angular/core';
import { Measurement } from '@app/interfaces/measurement';
import { Sensor } from '@app/interfaces/sensor';
import { TimeDelta } from '@app/interfaces/time-delta';
import { SensorService } from '@app/services/sensor.service';
import { Chart } from 'chart.js/auto';
// import { Math } from 'core-js';
import { oklch, formatHex } from 'culori';

@Component({
    selector: 'app-line-chart',
    imports: [],
    templateUrl: './line-chart.component.html',
    styleUrl: './line-chart.component.scss'
})
export class LineChartComponent implements OnInit, AfterViewInit {
  public chart: Chart = {} as Chart;
  @Input() sensor: Sensor = {} as Sensor;
  @Input() chartTitle: string = '';

  chartId: string = '';
  constructor(private sensorService: SensorService) {
    effect(() => {
      this.updateChart(this.sensorService.time_delta());
    });
  }

  ngOnInit() {
    this.chartId = Math.floor(Math.random() * 100000).toString();
  }

  ngAfterViewInit(): void {
    this.createChart();
  }

  private getColor(sensorId: number): string {
    var elem = document.getElementById(`sensor${sensorId}`);
    const color = elem
      ? formatHex(
          oklch(window.getComputedStyle(elem).getPropertyValue('color'))
        )
      : '#000000';
    console.log(color);
    return color || '#000000';
  }

  async createChart() {
    const measurements: Measurement[] =
      await this.sensorService.getSensorMeasurementsDelta(
        this.sensor.sensor_id,
        this.sensorService.time_delta()
      );

    const color = this.getColor(this.sensor.sensor_id);

    this.chart = new Chart(this.chartId, {
      type: 'line', //this denotes tha type of chart

      data: {
        // values on X-Axis
        labels: measurements.map((msr) => this.shortenTimestamp(msr.timestamp)),
        datasets: [
          {
            label: this.sensor.sensor_unit,
            data: measurements.map((msr) => msr.value),
            borderColor: color,
            backgroundColor: color + '40',
          },
        ],
      },

      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            onClick: null as any,
            position: 'bottom',
          },
        },
      },
    });
  }

  updateChart(time_delta: TimeDelta) {
    this.sensorService
      .getSensorMeasurementsDelta(this.sensor.sensor_id, time_delta)
      .then((measurements) => {
        this.chart.data.labels = measurements.map((msr) =>
          this.shortenTimestamp(msr.timestamp)
        );
        this.chart.data.datasets[0].data = measurements.map((msr) => msr.value);
        this.chart.update();
      });
  }

  shortenTimestamp(timestamp: string) {
    const timeSplit: string[] = timestamp.split('T');
    return `${timeSplit[0].substring(5, 7)}/${timeSplit[0].substring(
      8,
      10
    )} - ${timeSplit[1].substring(0, 2)}h${timeSplit[1].substring(3, 5)}`;
  }
}
