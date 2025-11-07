import { SensorType } from '../interfaces/sensor-type';
import { SENSOR_UNITS_CONFIG } from '../constants/constants';
import { Sensor } from '@app/interfaces/sensor';

export class SensorUnitsUtils {
  public static getDefaultUnit(sensorType: SensorType): string | undefined {
    return SENSOR_UNITS_CONFIG[sensorType]?.default;
  }

  public static getUnits(sensorType: SensorType): string[] {
    return SENSOR_UNITS_CONFIG[sensorType]?.available ?? [''];
  }

  public static convertUnitToPref(
    sensor: Sensor,
    value: number | undefined
  ): number {
    if (value === undefined || value === null) return 0;

    const config = SENSOR_UNITS_CONFIG[sensor.sensor_type];
    if (!config) return value;

    if (!config.available.includes(sensor.sensor_unit)) {
      console.warn(
        `Invalid unit ${sensor.sensor_unit} for ${sensor.sensor_type}`
      );
      return value;
    }

    const converted = config.convert(value, config.default, sensor.sensor_unit);
    const decimals = sensor.sensor_type === SensorType.ec ? 5 : 2;
    return parseFloat(converted.toFixed(decimals));
  }
}
