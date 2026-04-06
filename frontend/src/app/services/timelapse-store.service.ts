import { Injectable } from '@angular/core';
import { BehaviorSubject, map } from 'rxjs';

import { TimelapseMetadata } from '@app/interfaces/timelapse';

@Injectable({
  providedIn: 'root',
})
export class TimelapseStoreService {
  private readonly _timelapses$ = new BehaviorSubject<TimelapseMetadata[]>([]);
  readonly timelapses$ = this._timelapses$.asObservable();
  readonly empty$ = this._timelapses$.pipe(map(t => t.length === 0));

  getSnapshot(): TimelapseMetadata[] {
    return this._timelapses$.value;
  }

  setAll(timelapses: TimelapseMetadata[]): void {
    this._timelapses$.next([...timelapses]);
  }

  upsert(timelapse: TimelapseMetadata): void {
    const current = this._timelapses$.value;
    const idx = current.findIndex(t => t.id === timelapse.id);
    if (idx === -1) {
      this._timelapses$.next([timelapse, ...current]);
      return;
    }
    const next = [...current];
    next[idx] = { ...next[idx], ...timelapse };
    this._timelapses$.next(next);
  }

  remove(id: string): void {
    this._timelapses$.next(this._timelapses$.value.filter(t => t.id !== id));
  }
}
