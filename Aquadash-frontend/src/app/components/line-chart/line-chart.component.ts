import {
  AfterViewInit,
  Component,
  effect,
  Input,
  OnInit,
  ViewChild,
} from '@angular/core';
import { Measurement } from '@app/interfaces/measurement';
import { Sensor } from '@app/interfaces/sensor';
import { TimeDelta } from '@app/interfaces/time-delta';
import { SensorService } from '@app/services/sensor.service';
import { oklch, formatHex } from 'culori';
import {
  ChartComponent,
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexDataLabels,
  ApexTitleSubtitle,
  ApexStroke,
  ApexGrid,
  ApexAnnotations,
  NgApexchartsModule,
} from 'ng-apexcharts';

export type ChartOptions = {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  dataLabels: ApexDataLabels;
  grid: ApexGrid;
  stroke: ApexStroke;
  title: ApexTitleSubtitle;
  colors: string[];
};

@Component({
  selector: 'app-line-chart',
  standalone: true,
  imports: [NgApexchartsModule],
  templateUrl: './line-chart.component.html',
  styleUrls: ['./line-chart.component.scss'],
})
export class LineChartComponent implements AfterViewInit {
  @ViewChild('chart') chart!: ChartComponent;
  public chartOptions: ChartOptions;

  @Input() sensor: Sensor = {} as Sensor;
  @Input() chartTitle: string = '';

  constructor(private sensorService: SensorService) {
    this.chartOptions = {
      series: [],
      chart: {
        height: 250,
        type: 'line',
      },
      xaxis: {
        type: 'datetime',
      },
      dataLabels: {
        enabled: false,
      },
      grid: {
        padding: {
          right: 30,
          left: 20,
        },
      },
      stroke: {
        curve: 'straight',
      },
      title: {
        text: '',
        align: 'left',
      },
      colors: [],
    };
    effect(() => {
      const timeDelta = this.sensorService.time_delta();
      this.updateZoomRange(timeDelta);
    });
  }

  ngAfterViewInit(): void {
    this.loadInitialData();
  }

  private async loadInitialData() {
    const measurements = await this.sensorService.getSensorMeasurementsDelta(
      this.sensor.sensor_id,
      this.sensorService.time_delta()
    );
    console.log('Measurements: ', measurements);
    this.updateChartData(measurements);
  }

  public updateChart(timeDelta: TimeDelta) {
    this.sensorService
      .getSensorMeasurementsDelta(this.sensor.sensor_id, timeDelta)
      .then((measurements) => this.updateChartData(measurements));
  }

  private updateChartData(measurements: Measurement[]) {
    const color = this.getColor(this.sensor.sensor_id);
    const { start, end } = this.calculateDateRange(
      this.sensorService.time_delta()
    );
    console.log(measurements.map((msr) => msr.value));
    this.chartOptions = {
      series: [
        {
          name: this.sensor.sensor_unit,
          data: measurements.map((msr) => ({
            x: new Date(msr.timestamp).getTime(),
            y: msr.value,
          })),
        },
      ],
      chart: {
        height: 250,
        type: 'line',
      },
      xaxis: {
        type: 'datetime',
        min: start.getTime(),
        max: end.getTime(),
        labels: {
          formatter: (val) => this.formatDateLabel(new Date(val)),
        },
      },
      dataLabels: {
        enabled: false,
      },
      grid: {
        padding: {
          right: 30,
          left: 20,
        },
      },
      stroke: {
        curve: 'straight',
      },
      colors: [color],
      title: {
        text: this.chartTitle,
      },
    };

    this.chart.updateOptions(this.chartOptions);
    this.chart?.render();

    console.log(this.chartOptions);
    console.log(this.chart.series);
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

    if (this.chartOptions) {
      this.chartOptions.series = [
        {
          name: this.sensor.sensor_unit,
          data: measurements.map((msr) => msr.value),
        },
      ];
    }
    console.log(this.chartOptions);
  }

  shortenTimestamp(timestamp: string) {
    const timeSplit: string[] = timestamp.split('T');
    return `${timeSplit[0].substring(5, 7)}/${timeSplit[0].substring(
      8,
      10
    )} - ${timeSplit[1].substring(0, 2)}h${timeSplit[1].substring(3, 5)}`;
  }

  private formatDateLabel(date: Date): string {
    return `${date.getDate()}/${date.getMonth() + 1} ${date.getHours()}h${date
      .getMinutes()
      .toString()
      .padStart(2, '0')}`;
  }

  private calculateDateRange(timeDelta: TimeDelta): { start: Date; end: Date } {
    const endDate = new Date();
    const startDate = new Date(
      endDate.getTime() - this.timeDeltaToMs(timeDelta)
    );
    return { start: startDate, end: endDate };
  }

  private timeDeltaToMs(timeDelta: TimeDelta): number {
    return (
      timeDelta.days * 86400000 +
      timeDelta.hours * 3600000 +
      timeDelta.minutes * 60000 +
      timeDelta.seconds * 1000
    );
  }

  private updateZoomRange(timeDelta: TimeDelta) {
    if (!this.chart) return;

    const { start, end } = this.calculateDateRange(timeDelta);

    this.chart.updateOptions({
      xaxis: {
        min: start.getTime(),
        max: end.getTime(),
      },
    });
  }
}
