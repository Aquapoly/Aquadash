import { Component, Input, Output, EventEmitter } from '@angular/core';
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
import { SensorUnitsUtils } from '@app/utils/sensor-units.utils';

@Component({
  selector: 'app-line-chart',
  imports: [HighchartsChartModule],
  templateUrl: './line-chart.component.html',
  styleUrl: './line-chart.component.scss',
})
export class LineChartComponent {
  private themeSubscription!: Subscription;
  private thresholdDisplaySubscription!: Subscription;
  private thresholdDisplay: ChartThresholdDisplay =
    ChartThresholdDisplay.ColoredBackgroundWithLine;
  private lastAppliedUnit: string | null = null;
  private baseThresholds: {
    low: number;
    high: number;
    critLow: number;
    critHigh: number;
  } | null = null;

  protected theme: string = LIGHT_THEME;

  Highcharts: typeof Highcharts = Highcharts;
  chartConstructor: string = 'chart';
  chartOptions: Highcharts.Options = {};
  updateFlag: boolean = false;
  oneToOneFlag: boolean = true;
  runOutsideAngular: boolean = false;

  @Input() sensor: Sensor = {} as Sensor;
  @Input() chartTitle: string = '';
  @Input() unit: string = '';
  @Output() sensorUpdated = new EventEmitter<Sensor>();

  constructor(
    private readonly sensorService: SensorService,
    private readonly globalSettings: GlobalSettingsService
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
    this.globalSettings.sensorUnits$.subscribe(async (units) => {
      if (!this.sensor || !this.sensor.sensor_type) return;

      const preferred = units[this.sensor.sensor_type];
      if (!preferred) return;

      if (preferred !== this.lastAppliedUnit) {
        this.unit = preferred;
        await this.refreshChartWithNewUnits();
        this.lastAppliedUnit = preferred;
      }
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

  private async loadInitialData() {
    const measurements = await this.sensorService.getSensorMeasurementsDelta(
      this.sensor.sensor_id,
      this.sensorService.time_delta()
    );

    if (!this.baseThresholds) {
      this.baseThresholds = {
        low: this.sensor.threshold_low,
        high: this.sensor.threshold_high,
        critLow: this.sensor.threshold_critically_low,
        critHigh: this.sensor.threshold_critically_high,
      };
    }

    this.updateChartData(measurements);
  }

  private updateChartData(measurements: Measurement[]) {
    const backgroundThresholdOn: boolean =
      this.thresholdDisplay === ChartThresholdDisplay.ColoredBackground ||
      this.thresholdDisplay === ChartThresholdDisplay.ColoredBackgroundWithLine;
    const zonesOn: boolean =
      this.thresholdDisplay === ChartThresholdDisplay.ColoredLine ||
      this.thresholdDisplay === ChartThresholdDisplay.ColoredBackgroundWithLine;

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
        plotBands: backgroundThresholdOn
          ? this.createThresholds(this.sensor)
          : [],
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
          zones: zonesOn ? this.getZones() : [],
        },
      ],
    };
  }

  private async refreshChartWithNewUnits(): Promise<void> {
    console.log('[LineChart] refreshing chart with unit', this.unit);

    const measurements = await this.sensorService.getSensorMeasurementsDelta(
      this.sensor.sensor_id,
      this.sensorService.time_delta()
    );

    this.sensor.sensor_unit = this.unit;

    const convertedMeasurements = measurements.map((m) => ({
      ...m,
      value: SensorUnitsUtils.convertUnitToPref(this.sensor, m.value),
    }));

    const convertedSensor: Sensor = {
      ...this.sensor,
      threshold_low: SensorUnitsUtils.convertUnitToPref(
        this.sensor,
        this.baseThresholds!.low
      ),
      threshold_high: SensorUnitsUtils.convertUnitToPref(
        this.sensor,
        this.baseThresholds!.high
      ),
      threshold_critically_low: SensorUnitsUtils.convertUnitToPref(
        this.sensor,
        this.baseThresholds!.critLow
      ),
      threshold_critically_high: SensorUnitsUtils.convertUnitToPref(
        this.sensor,
        this.baseThresholds!.critHigh
      ),
      sensor_unit: this.unit,
    };

    this.sensor = convertedSensor;

    console.log('[LineChart] Sensor thresholds after conversion:', {
      unit: this.sensor.sensor_unit,
      critically_low: convertedSensor.threshold_critically_low,
      low: convertedSensor.threshold_low,
      high: convertedSensor.threshold_high,
      critically_high: convertedSensor.threshold_critically_high,
    });

    this.updateChartData(convertedMeasurements);

    const newYAxis: Highcharts.YAxisOptions = {
      title: { text: this.sensor.sensor_unit },
      labels: {
        style: {
          color: THEME_COLOR[this.theme].baseContent + 'a0',
        },
      },
      plotBands: this.createThresholds(this.sensor),
    };

    this.chartOptions = {
      ...this.chartOptions,
      yAxis: { ...newYAxis },
    };

    this.updateFlag = false;
    setTimeout(() => {
      this.updateFlag = true;
      console.log('[LineChart] redraw done');
    }, 0);

    this.sensorUpdated.emit(this.sensor);
  }

  private getZones(): Highcharts.SeriesZonesOptionsObject[] {
    return [
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
    ];
  }

  private createThresholds(sensor: Sensor): Highcharts.YAxisPlotBandsOptions[] {
    return [
      {
        from: sensor.threshold_critically_low - THRESHOLD_MARGIN,
        to: sensor.threshold_critically_low,
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
        from: sensor.threshold_critically_low,
        to: sensor.threshold_low,
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
        from: sensor.threshold_low,
        to: sensor.threshold_high,
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
        from: sensor.threshold_high,
        to: sensor.threshold_critically_high,
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
        from: sensor.threshold_critically_high,
        to: sensor.threshold_critically_high + THRESHOLD_MARGIN,
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
}
