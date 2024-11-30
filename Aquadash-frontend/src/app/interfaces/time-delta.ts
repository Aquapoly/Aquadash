export class TimeDelta {
    days: number = 0;
    hours: number = 0;
    minutes: number = 0;
    seconds: number = 0;

    constructor(days: number, hours: number, minutes: number, seconds: number) {
        this.days = days;
        this.hours = hours;
        this.minutes = minutes;
        this.seconds = seconds;
    }

    toString(): string {
        return `${this.days.toString().padStart(2, '0')}d,${this.hours.toString().padStart(2, '0')}:${this.minutes.toString().padStart(2, '0')}:${this.seconds.toString().padStart(2, '0')}`;
    }
}