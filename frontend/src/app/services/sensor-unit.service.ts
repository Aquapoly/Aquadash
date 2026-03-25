import { Injectable } from '@angular/core';
import { Sensor } from '@app/interfaces/sensor';
import { SensorType } from '@app/interfaces/sensor-type';
import {
  SensorDisplayUnit,
  SensorUnitDefinition,
  UnitConversionRule,
} from '@app/interfaces/sensor-unit';
import { SENSOR_UNIT_CONFIG } from '@app/constants/constants';

@Injectable({
  providedIn: 'root',
})
export class SensorUnitService {
  getUnitDefinition(sensorType: SensorType): SensorUnitDefinition | undefined {
    return SENSOR_UNIT_CONFIG[sensorType];
  }

  getAvailableUnits(sensorType: SensorType): SensorDisplayUnit[] {
    return this.getUnitDefinition(sensorType)?.availableUnits ?? [];
  }

  getDefaultUnit(sensorType: SensorType): SensorDisplayUnit | undefined {
    return this.getUnitDefinition(sensorType)?.defaultUnit;
  }

  convertValue(
    sensorType: SensorType,
    fromUnit: string,
    toUnit: string,
    value: number,
  ): number {
    if (fromUnit === toUnit) {
      return value;
    }

    const rule = this.getConversionRule(sensorType, fromUnit, toUnit);

    if (!rule) {
      return value;
    }

    if (rule.factor !== undefined) {
      return value * rule.factor;
    }

    if (rule.convert) {
      return rule.convert(value);
    }

    return value;
  }

  convertSensorValue(
    sensor: Sensor,
    value: number,
    displayUnit: string,
  ): number {
    return this.convertValue(
      sensor.sensor_type,
      sensor.sensor_unit,
      displayUnit,
      value,
    );
  }

  roundValue(value: number, decimals = 2): number {
    return Number(value.toFixed(decimals));
  }

  private getConversionRule(
    sensorType: SensorType,
    fromUnit: string,
    toUnit: string,
  ): UnitConversionRule | undefined {
    return this.getUnitDefinition(sensorType)?.conversions[fromUnit]?.[toUnit];
  }
}
