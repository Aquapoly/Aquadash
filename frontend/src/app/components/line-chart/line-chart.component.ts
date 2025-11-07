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
  private sensorStateSubscription!: Subscription;

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

  private viewSensor!: Sensor;

  constructor(
    private readonly sensorService: SensorService,
    private readonly globalSettings: GlobalSettingsService
  ) {}

  ngOnInit(): void {
    this.theme = this.globalSettings.getThemeName();
    this.viewSensor = { ...this.sensor };

    const savedUnit = this.globalSettings.getSensorUnit(
      this.viewSensor.sensor_type
    );

    if (savedUnit) {
      this.unit = savedUnit;
      this.lastAppliedUnit = savedUnit;
      this.viewSensor.sensor_unit = savedUnit;
    }

    this.sensorStateSubscription = this.globalSettings.sensorState$.subscribe(
      async (state) => {
        if (!this.viewSensor || !this.viewSensor.sensor_type) return;

        const preferredUnit = state.units[this.viewSensor.sensor_type];
        if (preferredUnit && preferredUnit !== this.lastAppliedUnit) {
          this.unit = preferredUnit;
          await this.refreshChartWithNewUnits();
          this.lastAppliedUnit = preferredUnit;
        }
      }
    );

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
    this.themeSubscription?.unsubscribe();
    this.thresholdDisplaySubscription?.unsubscribe();
    this.sensorStateSubscription?.unsubscribe();
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

    const defaultUnit = SensorUnitsUtils.getDefaultUnit(
      this.viewSensor.sensor_type
    );
    const needsConversion =
      this.unit && defaultUnit && this.unit !== defaultUnit;

    if (needsConversion) {
      const convertedMeasurements = this.convertMeasurements(measurements);
      this.viewSensor = this.convertSensorData(this.viewSensor);
      this.updateChartData(convertedMeasurements);
    } else {
      this.viewSensor = {
        ...this.viewSensor,
        threshold_low: this.baseThresholds.low,
        threshold_high: this.baseThresholds.high,
        threshold_critically_low: this.baseThresholds.critLow,
        threshold_critically_high: this.baseThresholds.critHigh,
        sensor_unit: defaultUnit || this.viewSensor.sensor_unit,
      };
      this.updateChartData(measurements);
    }
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
          text: this.viewSensor.sensor_unit,
        },
        minorGridLineWidth: 0,
        gridLineWidth: 0,
        plotBands: backgroundThresholdOn
          ? this.createThresholds(this.viewSensor)
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
        valueSuffix: this.viewSensor.sensor_unit,
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
          name: this.viewSensor.sensor_type,
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
    const measurements = await this.sensorService.getSensorMeasurementsDelta(
      this.sensor.sensor_id,
      this.sensorService.time_delta()
    );

    this.viewSensor.sensor_unit = this.unit;

    const convertedMeasurements = this.convertMeasurements(measurements);
    this.viewSensor = this.convertSensorData(this.viewSensor);

    this.updateChartData(convertedMeasurements);
    this.updateFlag = !this.updateFlag;
    this.sensorUpdated.emit(this.viewSensor);
  }

  private getZones(): Highcharts.SeriesZonesOptionsObject[] {
    return [
      {
        value: this.viewSensor.threshold_critically_low,
        color: THEME_COLOR[this.theme].danger,
      },
      {
        value: this.viewSensor.threshold_low,
        color: THEME_COLOR[this.theme].warning,
      },
      {
        value: this.viewSensor.threshold_high,
        color: THEME_COLOR[this.theme].success,
      },
      {
        value: this.viewSensor.threshold_critically_high,
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

  private convertSensorData(sensor: Sensor): Sensor {
    return {
      ...sensor,
      threshold_low: SensorUnitsUtils.convertUnitToPref(
        sensor,
        this.baseThresholds!.low
      ),
      threshold_high: SensorUnitsUtils.convertUnitToPref(
        sensor,
        this.baseThresholds!.high
      ),
      threshold_critically_low: SensorUnitsUtils.convertUnitToPref(
        sensor,
        this.baseThresholds!.critLow
      ),
      threshold_critically_high: SensorUnitsUtils.convertUnitToPref(
        sensor,
        this.baseThresholds!.critHigh
      ),
      sensor_unit: this.unit,
    };
  }

  private convertMeasurements(measurements: Measurement[]): Measurement[] {
    return measurements.map((m) => ({
      ...m,
      value: SensorUnitsUtils.convertUnitToPref(this.viewSensor, m.value),
    }));
  }
}
