import { Component, Input } from '@angular/core';
import { Sensor } from '@app/interfaces/sensor';
import { GlobalSettingsService } from '@app/services/global-settings.service/global-settings.service';
import { SensorService } from '@app/services/sensor.service';
import { Subscription } from 'rxjs';
import { THEME_COLOR } from '../../../constants/constants';
import { Measurement } from '@app/interfaces/measurement';
import { HighchartsChartModule } from 'highcharts-angular';
import * as Highcharts from 'highcharts';

export enum Theme {
  Light = 'light',
  Dark = 'dark',
}

@Component({
  selector: 'app-area-chart',
  imports: [HighchartsChartModule],
  templateUrl: './area-chart.component.html',
  styleUrl: './area-chart.component.scss',
})
export class AreaChartComponent {
  private themeSubscription!: Subscription;
  private theme: string = Theme.Light;

  Highcharts: typeof Highcharts = Highcharts;
  chartConstructor: string = 'chart';
  chartOptions: Highcharts.Options = {};
  updateFlag: boolean = false;
  oneToOneFlag: boolean = true;
  runOutsideAngular: boolean = false;

  @Input() sensor: Sensor = {} as Sensor;
  @Input() chartTitle: string = '';

  constructor(
    private sensorService: SensorService,
    private globalSettings: GlobalSettingsService
  ) {}

  ngOnInit(): void {
    this.theme = this.globalSettings.getThemeName();

    this.loadInitialData();
    this.themeSubscription = this.globalSettings.theme$.subscribe((theme) => {
      this.theme = theme;
      // if (this.chart) this.updateChartColors();
    });
  }

  ngAfterViewInit(): void {
    // if (!this.chart) return;

    this.updateChartColors();
  }

  ngOnDestroy(): void {
    if (this.themeSubscription) {
      this.themeSubscription.unsubscribe();
    }
  }

  private async updateChartColors(): Promise<void> {
    // this.chartOptions.annotations = this.createThresholdAnnotations(
    //   this.sensor
    // );
    // const foreColor = this.getForeColor();
    // const tooltipTheme = this.getTooltipTheme();
    // await this.chart.updateOptions({
    //   colors: [THEME_COLOR[this.theme].lineColor],
    //   annotations: this.createThresholdAnnotations(this.sensor),
    //   chart: {
    //     foreColor,
    //   },
    //   tooltip: {
    //     theme: tooltipTheme,
    //   },
    // });
    // await this.chart.render();
  }

  private async loadInitialData() {
    console.log('Loading initial data');
    const measurements = await this.sensorService.getSensorMeasurementsDelta(
      this.sensor.sensor_id,
      this.sensorService.time_delta()
    );
    console.log('Data loaded');

    this.updateChartData(measurements);
    await this.updateChartColors();

    // if (!this.chart) {
    //   return;
    // } else {
    //   console.log('Rendering chart with ', this.chartOptions);
    //   await this.chart.updateOptions(this.chartOptions);
    //   await this.chart.render();
    // }
  }

  private updateChartData(measurements: Measurement[]) {
    this.chartOptions = {
      chart: {
        type: 'spline',
        zooming: {
          type: 'x',
        },
      },
      title: {
        text: this.chartTitle,
        align: 'left',
      },
      xAxis: {
        type: 'datetime',
      },
      yAxis: {
        title: {
          text: this.sensor.sensor_unit,
        },
        minorGridLineWidth: 0,
        gridLineWidth: 0,
        plotBands: this.createThresholds(this.sensor),
      },
      legend: {
        enabled: false,
      },
      tooltip: {
        valueSuffix: this.sensor.sensor_unit,
      },
      plotOptions: {
        spline: {
          lineWidth: 8,
          states: {
            hover: {
              lineWidth: 12,
            },
          },
          marker: {
            enabled: true,
          },
          pointInterval: 3600000, // one hour
          pointStart: '2014-02-29',
        },
      },

      series: [
        {
          type: 'line',
          color: THEME_COLOR[this.theme].lineColor,
          name: this.sensor.sensor_type,
          data: measurements.map((msr) => ({
            x: new Date(msr.timestamp).getTime(),
            y: msr.value,
          })),
          lineWidth: 3,
          zones: [
            {
              value: this.sensor.threshold_critically_low,
              color: THEME_COLOR[this.theme].danger,
            },
            {
              value: this.sensor.threshold_low,
              color: THEME_COLOR[this.theme].warning,
            },
            {
              value: this.sensor.threshold_high,
              color: THEME_COLOR[this.theme].success,
            },
            {
              value: this.sensor.threshold_critically_high,
              color: THEME_COLOR[this.theme].warning,
            },
            {
              color: THEME_COLOR[this.theme].danger,
            },
          ],
        },
      ],
    };
  }

  private createThresholds(sensor: Sensor): Highcharts.YAxisPlotBandsOptions[] {
    return [
      {
        from: sensor.threshold_critically_low - 100,
        to: sensor.threshold_critically_low,
        color: THEME_COLOR[this.theme].danger + '20',
        label: {
          text: 'Critically Low',
          style: {
            color: THEME_COLOR[this.theme].danger,
          },
        },
      },
      {
        from: sensor.threshold_critically_low,
        to: sensor.threshold_low,
        color: THEME_COLOR[this.theme].warning + '0a',
        label: {
          text: 'Low',
          style: {
            color: THEME_COLOR[this.theme].warning,
          },
        },
      },
      {
        from: sensor.threshold_low,
        to: sensor.threshold_high,
        color: THEME_COLOR[this.theme].success + '10',
        label: {
          text: 'Normal',
          style: {
            color: THEME_COLOR[this.theme].success,
          },
        },
      },
      {
        from: sensor.threshold_high,
        to: sensor.threshold_critically_high,
        color: THEME_COLOR[this.theme].warning + '0a',
        label: {
          text: 'High',
          style: {
            color: THEME_COLOR[this.theme].warning,
          },
        },
      },
      {
        from: sensor.threshold_critically_high,
        to: sensor.threshold_critically_high + 100,
        color: THEME_COLOR[this.theme].danger + '20',
        label: {
          text: 'Critically High',
          style: {
            color: THEME_COLOR[this.theme].danger,
          },
        },
      },
    ];
  }

  private createThresholdAnnotations(sensor: Sensor): ApexAnnotations {
    return {};
    // return {
    //   yaxis: [
    //     this.createCriticalLowAnnotation(sensor),
    //     this.createNormalRangeAnnotation(sensor),
    //     this.createCriticalHighAnnotation(sensor),
    //   ],
    // };
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
    const opacity = labelText ? 0.2 : 0.05;
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

  // private calculateDateRange(timeDelta: TimeDelta): { start: Date; end: Date } {
  //   const endDate = new Date();
  //   const startDate = new Date(
  //     endDate.getTime() - this.timeDeltaToMs(timeDelta)
  //   );
  //   return { start: startDate, end: endDate };
  // }

  // private timeDeltaToMs(timeDelta: TimeDelta): number {
  //   return (
  //     timeDelta.days * 86400000 +
  //     timeDelta.hours * 3600000 +
  //     timeDelta.minutes * 60000 +
  //     timeDelta.seconds * 1000
  //   );
  // }

  // private getForeColor(): string {
  //   return this.theme === DARK_THEME ? '#ddd' : '#222';
  // }

  // private getTooltipTheme(): string {
  //   return this.theme === DARK_THEME ? 'dark' : 'light';
  // }
}
