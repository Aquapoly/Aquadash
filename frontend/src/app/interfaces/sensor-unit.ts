import { SensorType } from './sensor-type';

export enum TemperatureUnit {
  Celsius = 'Celsius',
  Fahrenheit = 'Fahrenheit',
  Kelvin = 'Kelvin',
}

export enum EcUnit {
  MilliSiemensPerCm = 'mS/cm',
  MicroSiemensPerCm = 'μS/cm',
}

export type SensorDisplayUnit = TemperatureUnit | EcUnit;

export interface UnitConversionRule {
  factor?: number;
  convert?: (value: number) => number;
}

export type UnitConversionMap = {
  [fromUnit: string]: {
    [toUnit: string]: UnitConversionRule;
  };
};

export interface SensorUnitDefinition {
  defaultUnit: SensorDisplayUnit;
  availableUnits: SensorDisplayUnit[];
  conversions: UnitConversionMap;
}

export type SensorUnitConfig = Partial<
  Record<SensorType, SensorUnitDefinition>
>;
