import {
  AfterViewInit,
  Component,
  effect,
  Input,
  OnDestroy,
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
import { LIGHT_THEME, THEME_COLOR } from '../../../constants/constants';
import { GlobalSettingsService } from '@app/services/global-settings.service/global-settings.service';
import { Subscription } from 'rxjs';

export type ChartOptions = {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  dataLabels: ApexDataLabels;
  grid: ApexGrid;
  stroke: ApexStroke;
  title: ApexTitleSubtitle;
  colors: string[];
  annotations: ApexAnnotations;
};

@Component({
  selector: 'app-line-chart',
  standalone: true,
  imports: [NgApexchartsModule],
  templateUrl: './line-chart.component.html',
  styleUrls: ['./line-chart.component.scss'],
})
export class LineChartComponent implements AfterViewInit, OnInit, OnDestroy {
  @ViewChild('chart') chart!: ChartComponent;
  public chartOptions: ChartOptions;
  private themeSubscription!: Subscription;
  private theme: string = 'light';

  @Input() sensor: Sensor = {} as Sensor;
  @Input() chartTitle: string = '';

  constructor(
    private sensorService: SensorService,
    private globalSettings: GlobalSettingsService
  ) {
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
        padding: {},
      },
      stroke: {
        curve: 'smooth',
      },
      title: {
        text: '',
        align: 'left',
      },
      colors: [],
      annotations: {},
    };
    effect(() => {
      const timeDelta = this.sensorService.time_delta();
      this.updateZoomRange(timeDelta);
    });
  }

  ngOnInit(): void {
    this.theme = this.globalSettings.getThemeName();
    this.themeSubscription = this.globalSettings.theme$.subscribe((theme) => {
      this.theme = theme;
      console.log('Theme updated:', theme);
      this.updateChartColors();
    });
  }

  ngAfterViewInit(): void {
    console.log('ngAfterViewInit', this.sensor);
    this.loadInitialData();
  }

  ngOnDestroy(): void {
    if (this.themeSubscription) {
      this.themeSubscription.unsubscribe();
    }
  }

  private updateChartColors(): void {
    if (!this.chart) return;

    this.chartOptions.annotations = this.createThresholdAnnotations(
      this.sensor
    );
    this.chartOptions.colors = [THEME_COLOR[this.theme].lineColor];

    this.chart.updateOptions({
      colors: [THEME_COLOR[this.theme].lineColor],
      annotations: this.createThresholdAnnotations(this.sensor),
    });

    console.log(
      'Chart colors updated:',
      THEME_COLOR[this.theme].lineColor,
      this.chartOptions
    );

    this.chart.render();
  }

  public async loadInitialData() {
    const measurements = await this.sensorService.getSensorMeasurementsDelta(
      this.sensor.sensor_id,
      this.sensorService.time_delta()
    );

    this.updateChartData(measurements);
    this.updateChartColors();
    this.chart?.render();
  }

  public updateChart(timeDelta: TimeDelta) {
    this.sensorService
      .getSensorMeasurementsDelta(this.sensor.sensor_id, timeDelta)
      .then((measurements) => this.updateChartData(measurements));
  }

  private updateChartData(measurements: Measurement[]) {
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
        padding: {},
      },
      stroke: {
        curve: 'smooth',
      },
      colors: [THEME_COLOR[this.theme].lineColor],
      title: {
        text: this.chartTitle,
      },
      annotations: this.createThresholdAnnotations(this.sensor),
    };

    console.log(this.chartOptions);

    this.chart.updateOptions(this.chartOptions);
    this.chart?.render();
  }

  async createChart() {
    const measurements: Measurement[] =
      await this.sensorService.getSensorMeasurementsDelta(
        this.sensor.sensor_id,
        this.sensorService.time_delta()
      );

    if (this.chartOptions) {
      this.chartOptions.series = [
        {
          name: this.sensor.sensor_unit,
          data: measurements.map((msr) => msr.value),
        },
      ];
    }
    console.log(this.chartOptions);
    console.log(this.chart);
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

  private createThresholdAnnotations(sensor: Sensor): ApexAnnotations {
    const opacity = this.theme === LIGHT_THEME ? 0.1 : 0.05;
    return {
      yaxis: [
        {
          y: sensor.threshold_critically_low,
          y2: sensor.threshold_low,
          fillColor: THEME_COLOR[this.theme].warning,
          borderColor: THEME_COLOR[this.theme].success,
          opacity: opacity,
        },
        {
          y: sensor.threshold_low,
          y2: sensor.threshold_high,
          fillColor: THEME_COLOR[this.theme].success,
          borderColor: THEME_COLOR[this.theme].success,
          opacity: opacity + 0.1,
        },
        {
          y: sensor.threshold_high,
          y2: sensor.threshold_critically_high,
          fillColor: THEME_COLOR[this.theme].warning,
          borderColor: THEME_COLOR[this.theme].success,
          opacity: opacity,
        },
      ],
    };
  }
}
