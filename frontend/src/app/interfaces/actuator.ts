export interface Actuator {
    actuator_id: number;
    actuator_name: string;
    actuator_type: string;
    low: number;
    high: number;
    enabled: boolean;
    activation_condition: string;
    activation_period: number;
    activation_duration: number;
    last_activated:Date;
}