import { Component, Input } from '@angular/core';
import { Sensor } from '@app/interfaces/sensor';
import { GlobalSettingsService } from '@app/services/global-settings.service/global-settings.service';
import { SensorService } from '@app/services/sensor.service';
import { Subscription } from 'rxjs';
import { LIGHT_THEME, THEME_COLOR } from '../../../constants/constants';
import { Measurement } from '@app/interfaces/measurement';
import { HighchartsChartModule } from 'highcharts-angular';
import * as Highcharts from 'highcharts';
import DarkBlueTheme from 'highcharts/themes/dark-blue';
import GridLightTheme from 'highcharts/themes/brand-light';
import { NgClass } from '@angular/common';

@Component({
  selector: 'app-area-chart',
  imports: [HighchartsChartModule],
  templateUrl: './area-chart.component.html',
  styleUrl: './area-chart.component.scss',
})
export class AreaChartComponent {
  private themeSubscription!: Subscription;
  protected theme: string = LIGHT_THEME;

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
      this.loadInitialData();
    });
  }

  ngAfterViewInit(): void {}

  ngOnDestroy(): void {
    if (this.themeSubscription) {
      this.themeSubscription.unsubscribe();
    }
  }

  private async loadInitialData() {
    const measurements = await this.sensorService.getSensorMeasurementsDelta(
      this.sensor.sensor_id,
      this.sensorService.time_delta()
    );

    this.updateChartData(measurements);
  }

  private updateChartData(measurements: Measurement[]) {
    this.chartOptions = {
      chart: {
        type: 'spline',
        zooming: {
          type: 'x',
        },
        backgroundColor: '#0000',
      },
      title: {
        text: this.chartTitle,
        align: 'left',
        style: {
          color: THEME_COLOR[this.theme].baseContent,
        },
      },
      xAxis: {
        type: 'datetime',
        labels: {
          style: {
            color: THEME_COLOR[this.theme].baseContent + 'a0',
          },
        },
      },
      yAxis: {
        title: {
          text: this.sensor.sensor_unit,
        },
        minorGridLineWidth: 0,
        gridLineWidth: 0,
        plotBands: this.createThresholds(this.sensor),
        labels: {
          style: {
            color: THEME_COLOR[this.theme].baseContent + 'a0',
          },
        },
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
        color: THEME_COLOR[this.theme].warning + '10',
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
        color: THEME_COLOR[this.theme].warning + '10',
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
}
