import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'duration'
})
export class DurationPipe implements PipeTransform {
  transform(durationSeconds: number): string {
    if (durationSeconds < 5) return durationSeconds.toFixed(2) + 's';
    if (durationSeconds < 120) return durationSeconds.toFixed(0) + 's';
    
    let durationMinutes: number = Math.floor(durationSeconds / 60);
    durationSeconds = durationSeconds - durationMinutes * 60;

    if (durationMinutes < 60) return durationMinutes.toFixed(0) + 'm' + durationSeconds.toFixed(0) + 's';

    let durationHours: number = Math.floor(durationMinutes / 60);
    durationMinutes = durationMinutes - durationHours * 60;
    if (durationHours < 24) return durationHours.toFixed(0) + 'h' + durationMinutes.toFixed(0) + 'm';

    const durationDays: number = Math.floor(durationHours / 24);
    durationHours = durationHours - durationDays * 24;
    if (durationDays < 7) return durationDays.toFixed(0) + 'j' + durationHours.toFixed(0) + 'h';
    
    return durationDays.toFixed(0) + 'j';
  }
}
