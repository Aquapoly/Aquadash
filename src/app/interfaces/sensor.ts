import { SensorType } from "./sensor-type";

export interface Sensor {
    sensor_type: SensorType;
    prototype_id: number;
    sensor_id: number;
    sensor_unit: string;
    threshold_critically_low: number;
    threshold_low: number;
    threshold_high: number;
    threshold_critically_high: number;
}