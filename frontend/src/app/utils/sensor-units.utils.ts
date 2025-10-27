import { SensorType } from '../interfaces/sensor-type';
import { TemperatureUnit, EcUnit } from '../constants/constants';
import { Sensor } from '@app/interfaces/sensor';

// Pour ajouter un nouveau capteur et permettre différentes unités:
// Ajouter :
// - une entrée dans defaultUnits
// - une case dans getUnits()
// - et une fonction de conversion

export class SensorUnitsUtils {
  public static defaultUnits: Map<SensorType, string> = new Map<
    SensorType,
    string
  >([
    [SensorType.temperature, TemperatureUnit.Celsius],
    [SensorType.ec, EcUnit.MicroSiemensPerCm],
  ]);

  public static getDefaultUnit(sensorType: SensorType): string | undefined {
    return this.defaultUnits.get(sensorType);
  }

  public static getUnits(sensorType: SensorType): string[] {
    switch (sensorType) {
      case SensorType.temperature:
        return Object.values(TemperatureUnit);
      case SensorType.ec:
        return Object.values(EcUnit);
      default:
        return [this.getDefaultUnit(sensorType) ?? ''];
    }
  }

  public static convertUnitToPref(
    sensor: Sensor,
    value: number | undefined
  ): number {
    if (value === undefined) return 0;

    const currentUnit = sensor.sensor_unit;
    const defaultUnit = this.getDefaultUnit(sensor.sensor_type);

    if (!defaultUnit || currentUnit === defaultUnit)
      return parseFloat(value.toFixed(2));

    let convertedValue = value;

    switch (sensor.sensor_type) {
      case SensorType.temperature:
        convertedValue = this.convertTemperature(
          defaultUnit,
          currentUnit,
          value
        );
        break;
      case SensorType.ec:
        convertedValue = this.convertEc(defaultUnit, currentUnit, value);
        break;
    }

    return parseFloat(convertedValue.toFixed(2));
  }

  private static convertTemperature(
    defaultUnit: string,
    currentUnit: string,
    value: number
  ): number {
    if (
      defaultUnit === TemperatureUnit.Celsius &&
      currentUnit === TemperatureUnit.Fahrenheit
    ) {
      return value * 1.8 + 32; // C → F
    }
    return value;
  }

  private static convertEc(
    defaultUnit: string,
    currentUnit: string,
    value: number
  ): number {
    if (
      defaultUnit === EcUnit.MicroSiemensPerCm &&
      currentUnit === EcUnit.MilliSiemensPerCm
    ) {
      return value * 1000; // µS → mS
    }
    return value;
  }
}
