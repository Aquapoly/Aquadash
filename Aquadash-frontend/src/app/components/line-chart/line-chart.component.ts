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
import {
  DARK_THEME,
  LIGHT_THEME,
  THEME_COLOR,
} from '../../../constants/constants';
import { GlobalSettingsService } from '@app/services/global-settings.service/global-settings.service';
import { Subscription } from 'rxjs';
import { h } from '@angular/core/navigation_types.d-u4EOrrdZ';

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
  tooltip: ApexTooltip;
};

export enum Theme {
  Light = 'light',
  Dark = 'dark',
}

export const BASE_CHART_OPTIONS: ChartOptions = {
  series: [],
  chart: {
    height: 250,
    type: 'area',
    foreColor: '#222',
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
  tooltip: {
    theme: Theme.Light,
  },
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
  public chartOptions: ChartOptions = { ...BASE_CHART_OPTIONS };
  private themeSubscription!: Subscription;
  private theme: string = Theme.Light;

  @Input() sensor: Sensor = {} as Sensor;
  @Input() chartTitle: string = '';

  constructor(
    private sensorService: SensorService,
    private globalSettings: GlobalSettingsService
  ) {}

  ngOnInit(): void {
    this.theme = this.globalSettings.getThemeName();
    this.chartOptions.chart.foreColor = this.getForeColor();
    this.chartOptions.tooltip.theme = this.getTooltipTheme();

    this.loadInitialData();
    this.themeSubscription = this.globalSettings.theme$.subscribe((theme) => {
      this.theme = theme;
      if (this.chart) this.updateChartColors();
    });
  }

  ngAfterViewInit(): void {
    if (!this.chart) {
      console.log('NO CHART');
      return;
    }
    this.updateChartColors();
    this.chart?.render();
  }

  ngOnDestroy(): void {
    if (this.themeSubscription) {
      this.themeSubscription.unsubscribe();
    }
  }

  private updateChartColors(): void {
    this.chartOptions.annotations = this.createThresholdAnnotations(
      this.sensor
    );
    const foreColor = this.getForeColor();
    const tooltipTheme = this.getTooltipTheme();

    this.chart.updateOptions({
      colors: [THEME_COLOR[this.theme].lineColor],
      annotations: this.createThresholdAnnotations(this.sensor),
      chart: {
        foreColor,
      },
      tooltip: {
        theme: tooltipTheme,
      },
    });
  }

  private async loadInitialData() {
    console.log('Loading initial data');
    const measurements = await this.sensorService.getSensorMeasurementsDelta(
      this.sensor.sensor_id,
      this.sensorService.time_delta()
    );
    console.log('Data loaded');

    this.updateChartData(measurements);
    this.updateChartColors();

    if (!this.chart) {
      console.log('NO CHART');
      return;
    } else {
      console.log('Rendering chart with ', this.chartOptions);
      this.chart.updateOptions(this.chartOptions);
      this.chart.render();
    }
  }

  private updateChartData(measurements: Measurement[]) {
    const { start, end } = this.calculateDateRange(
      this.sensorService.time_delta()
    );

    this.chartOptions = {
      ...BASE_CHART_OPTIONS,
      series: [
        {
          name: this.sensor.sensor_unit,
          data: measurements.map((msr) => ({
            x: new Date(msr.timestamp).getTime(),
            y: msr.value,
          })),
        },
      ],
      xaxis: {
        ...BASE_CHART_OPTIONS.xaxis,
        min: start.getTime(),
        max: end.getTime(),
        labels: {
          formatter: (val) => this.formatDateLabel(new Date(val)),
        },
      },
      colors: [THEME_COLOR[this.theme].lineColor],
      title: {
        text: this.chartTitle,
      },
      annotations: this.createThresholdAnnotations(this.sensor),
      tooltip: {
        theme: this.getTooltipTheme(),
      },
    };

    console.log(this.chartOptions);
  }

  private createThresholdAnnotations(sensor: Sensor): ApexAnnotations {
    return {
      yaxis: [
        this.createCriticalLowAnnotation(sensor),
        this.createNormalRangeAnnotation(sensor),
        this.createCriticalHighAnnotation(sensor),
      ],
    };
  }

  private createCriticalLowAnnotation(sensor: Sensor) {
    return this.createAnnotation(
      sensor.threshold_critically_low,
      sensor.threshold_low,
      THEME_COLOR[this.theme].warning
    );
  }

  private createNormalRangeAnnotation(sensor: Sensor) {
    return this.createAnnotation(
      sensor.threshold_low,
      sensor.threshold_high,
      THEME_COLOR[this.theme].success,
      'Normal'
    );
  }

  private createCriticalHighAnnotation(sensor: Sensor) {
    return this.createAnnotation(
      sensor.threshold_high,
      sensor.threshold_critically_high,
      THEME_COLOR[this.theme].warning
    );
  }

  private createAnnotation(
    y: number,
    y2: number,
    fillColor: string,
    labelText?: string
  ) {
    const opacity = labelText ? 0.3 : 0.1;
    return {
      y,
      y2,
      fillColor,
      borderColor: THEME_COLOR[this.theme].success,
      opacity,
      ...(labelText && {
        label: {
          text: labelText,
          offsetY: 0,
          style: {
            color: '#fff',
            background: fillColor + '80',
          },
        },
      }),
    };
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

  private getForeColor(): string {
    return this.theme === DARK_THEME ? '#ddd' : '#222';
  }

  private getTooltipTheme(): string {
    return this.theme === DARK_THEME ? 'dark' : 'light';
  }
}
