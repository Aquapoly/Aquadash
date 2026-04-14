import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { Sensor } from '@app/interfaces/sensor';
import { GlobalSettingsService } from '@app/services/global-settings.service/global-settings.service';
import { SensorService } from '@app/services/sensor.service';
import { Subscription } from 'rxjs';
import {
  ChartThresholdDisplay,
  LIGHT_THEME,
  LIMIT as THRESHOLD_MARGIN,
  THEME_COLOR,
  ThresholdNames,
  ThresholdsBackgroundOpacity,
} from '@app/constants/constants';
import { Measurement } from '@app/interfaces/measurement';
import { HighchartsChartModule } from 'highcharts-angular';
import * as Highcharts from 'highcharts';
import { SensorUnitService } from '@app/services/sensor-unit.service';
import { SensorDisplayUnit } from '@app/interfaces/sensor-unit';

@Component({
  selector: 'app-line-chart',
  imports: [HighchartsChartModule],
  templateUrl: './line-chart.component.html',
  styleUrl: './line-chart.component.scss',
})
export class LineChartComponent implements OnChanges {
  private themeSubscription!: Subscription;
  private thresholdDisplaySubscription!: Subscription;
  private thresholdDisplay: ChartThresholdDisplay =
    ChartThresholdDisplay.ColoredBackgroundWithLine;
  protected theme: string = LIGHT_THEME;

  Highcharts: typeof Highcharts = Highcharts;
  chartConstructor: string = 'chart';
  chartOptions: Highcharts.Options = {};
  updateFlag: boolean = false;
  oneToOneFlag: boolean = true;
  runOutsideAngular: boolean = false;

  @Input() sensor: Sensor = {} as Sensor;
  @Input() chartTitle: string = '';
  @Input() displayUnit: SensorDisplayUnit | string = '';
  @Input() refreshToken: number = 0;

  constructor(
    private readonly sensorService: SensorService,
    private readonly globalSettings: GlobalSettingsService,
    private readonly sensorUnitService: SensorUnitService,
  ) {}

  ngOnInit(): void {
    this.theme = this.globalSettings.getThemeName();

    this.loadInitialData();
    this.themeSubscription = this.globalSettings.theme$.subscribe((theme) => {
      this.theme = theme;
      this.loadInitialData();
    });
    this.thresholdDisplaySubscription =
      this.globalSettings.thresholdDisplay$.subscribe((display) => {
        this.thresholdDisplay = display;
        this.loadInitialData();
      });
  }

  ngOnDestroy(): void {
    if (this.themeSubscription) {
      this.themeSubscription.unsubscribe();
    }
    if (this.thresholdDisplaySubscription) {
      this.thresholdDisplaySubscription.unsubscribe();
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    const displayUnitChanged =
      changes['displayUnit'] && !changes['displayUnit'].firstChange;
    const refreshTokenChanged =
      changes['refreshToken'] && !changes['refreshToken'].firstChange;

    if (displayUnitChanged || refreshTokenChanged) {
      this.loadInitialData();
    }
  }

  private async loadInitialData() {
    const measurements = await this.sensorService.getSensorMeasurementsDelta(
      this.sensor.sensor_id,
      this.sensorService.time_delta(),
    );

    this.updateChartData(measurements);
  }

  private updateChartData(measurements: Measurement[]) {
    const backgroundThresholdOn: boolean =
      this.thresholdDisplay === ChartThresholdDisplay.ColoredBackground ||
      this.thresholdDisplay === ChartThresholdDisplay.ColoredBackgroundWithLine;

    const zonesOn: boolean =
      this.thresholdDisplay === ChartThresholdDisplay.ColoredLine ||
      this.thresholdDisplay === ChartThresholdDisplay.ColoredBackgroundWithLine;

    const displayedUnit = this.displayUnit || this.sensor.sensor_unit;

    this.chartOptions = {
      time: {
        timezone: undefined,
      },
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
          text: displayedUnit,
        },
        minorGridLineWidth: 0,
        gridLineWidth: 0,
        plotBands: backgroundThresholdOn ? this.createThresholds() : [],
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
        valueSuffix: displayedUnit,
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
            y: this.convertAndRoundValue(msr.value),
          })),
          lineWidth: 3,
          zones: zonesOn ? this.getZones() : [],
        },
      ],
    };

    this.updateFlag = true;
  }

  private getZones(): Highcharts.SeriesZonesOptionsObject[] {
    return [
      {
        value: this.convertAndRoundValue(this.sensor.threshold_critically_low),
        color: THEME_COLOR[this.theme].danger,
      },
      {
        value: this.convertAndRoundValue(this.sensor.threshold_low),
        color: THEME_COLOR[this.theme].warning,
      },
      {
        value: this.convertAndRoundValue(this.sensor.threshold_high),
        color: THEME_COLOR[this.theme].success,
      },
      {
        value: this.convertAndRoundValue(this.sensor.threshold_critically_high),
        color: THEME_COLOR[this.theme].warning,
      },
      {
        color: THEME_COLOR[this.theme].danger,
      },
    ];
  }

  private createThresholds(): Highcharts.YAxisPlotBandsOptions[] {
    const criticallyLow = this.convertAndRoundValue(
      this.sensor.threshold_critically_low,
    );
    const low = this.convertAndRoundValue(this.sensor.threshold_low);
    const high = this.convertAndRoundValue(this.sensor.threshold_high);
    const criticallyHigh = this.convertAndRoundValue(
      this.sensor.threshold_critically_high,
    );

    const convertedMargin = this.getConvertedMargin();

    return [
      {
        from: criticallyLow - convertedMargin,
        to: criticallyLow,
        color:
          THEME_COLOR[this.theme].danger + ThresholdsBackgroundOpacity.Critical,
        label: {
          text: ThresholdNames.CriticallyLow,
          style: {
            color: THEME_COLOR[this.theme].danger,
          },
        },
      },
      {
        from: criticallyLow,
        to: low,
        color:
          THEME_COLOR[this.theme].warning + ThresholdsBackgroundOpacity.Normal,
        label: {
          text: ThresholdNames.Low,
          style: {
            color: THEME_COLOR[this.theme].warning,
          },
        },
      },
      {
        from: low,
        to: high,
        color:
          THEME_COLOR[this.theme].success + ThresholdsBackgroundOpacity.Normal,
        label: {
          text: ThresholdNames.Normal,
          style: {
            color: THEME_COLOR[this.theme].success,
          },
        },
      },
      {
        from: high,
        to: criticallyHigh,
        color:
          THEME_COLOR[this.theme].warning + ThresholdsBackgroundOpacity.Normal,
        label: {
          text: ThresholdNames.High,
          style: {
            color: THEME_COLOR[this.theme].warning,
          },
        },
      },
      {
        from: criticallyHigh,
        to: criticallyHigh + convertedMargin,
        color:
          THEME_COLOR[this.theme].danger + ThresholdsBackgroundOpacity.Critical,
        label: {
          text: ThresholdNames.CriticallyHigh,
          style: {
            color: THEME_COLOR[this.theme].danger,
          },
        },
      },
    ];
  }

  private convertAndRoundValue(value: number): number {
    const unitToDisplay = this.displayUnit || this.sensor.sensor_unit;

    const convertedValue = this.sensorUnitService.convertSensorValue(
      this.sensor,
      value,
      unitToDisplay,
    );

    return this.sensorUnitService.roundValue(convertedValue);
  }

  private getConvertedMargin(): number {
    const displayedUnit = this.displayUnit || this.sensor.sensor_unit;

    const convertedMargin = this.sensorUnitService.convertValue(
      this.sensor.sensor_type,
      this.sensor.sensor_unit,
      displayedUnit,
      THRESHOLD_MARGIN,
    );

    return this.sensorUnitService.roundValue(convertedMargin);
  }
}
