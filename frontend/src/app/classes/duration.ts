import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'duration'
})
export class DurationPipe implements PipeTransform {
  transform(durationSeconds: number): string {
    if (durationSeconds < 5) return durationSeconds.toFixed(2) + 's';
    if (durationSeconds < 120) return durationSeconds.toFixed(0) + 's';
    
    const durationMinutes: number = Math.floor(durationSeconds / 60);
    durationSeconds = durationSeconds - durationMinutes * 60;

    return durationMinutes.toFixed(0) + 'm' + durationSeconds.toFixed(0) + 's';
  }
}
