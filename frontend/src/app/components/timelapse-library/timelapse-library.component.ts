import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Pipe, PipeTransform } from '@angular/core';
import { Observable } from 'rxjs';

import { SERVER_URL } from '@app/environment';
import { TimelapseMetadata } from '@app/interfaces/timelapse';
import { DurationPipe } from '@app/classes/duration';
import { TimelapseStoreService } from '@app/services/timelapse-store.service';
import { TimelapseMetadataDto } from '@app/interfaces/timelapse.dto';
import { mapTimelapseMetadataDto } from '@app/interfaces/timelapse.mapper';

@Pipe({
  name: 'statusText',
  standalone: true,
})
export class StatusTextPipe implements PipeTransform {
  transform(timelapse: TimelapseMetadata): string {
    if (timelapse.ready === undefined || timelapse.ready === null) return 'Inconnu';
    return timelapse.ready ? 'Terminé' : 'Enregistrement';
  }
}

@Pipe({
  name: 'timelapseSeconds',
  standalone: true,
})
export class TimelapseSecondsPipe implements PipeTransform {
  transform(timelapse: TimelapseMetadata): number {
    if (!timelapse.start_date) return NaN;
    const start: Date = timelapse.start_date;

    if (timelapse.latest_frame_date) {
      const diffMilli = timelapse.latest_frame_date.getTime() - start.getTime();
      return Math.max(0, diffMilli / 1000);
    }

    return 0;
  }
}

@Component({
  selector: 'app-timelapse-library',
  standalone: true,
  imports: [CommonModule, StatusTextPipe, TimelapseSecondsPipe, DurationPipe],
  templateUrl: './timelapse-library.component.html',
  styleUrl: './timelapse-library.component.css'
})
export class TimelapseLibraryComponent implements OnInit{
  readonly timelapses$: Observable<TimelapseMetadata[]>;
  readonly timelapsesEmpty$: Observable<boolean>;
  error: string | null = null;

  constructor(private http: HttpClient, private store: TimelapseStoreService) {
    this.timelapses$ = this.store.timelapses$;
    this.timelapsesEmpty$ = this.store.empty$;
  }

  ngOnInit(): void {
    this.http.get<TimelapseMetadataDto[]>(`${SERVER_URL}/timelapse`).subscribe({
      next: (response: TimelapseMetadataDto[]) => {
        this.store.setAll(response.map(t => mapTimelapseMetadataDto(t)));
      },
      error: (err) => {
        this.error = `Échec de l'obtention de la liste des timelapses: ${err.error?.detail || err.message}`;
      }
    });
  }

  download(timelapse: TimelapseMetadata) {
    window.open(`${SERVER_URL}/timelapse/${timelapse.id}/download`, '_blank');
  }

  delete(timelapse: TimelapseMetadata) {
    if (confirm(`Êtes-vous sûr de vouloir supprimer "${timelapse.name}"?`)) {
      this.http.delete(`${SERVER_URL}/timelapse/${timelapse.id}`).subscribe({
        next: () => {
          this.store.remove(timelapse.id);
        },
        error: (err) => {
          alert('Échec de la suppression du timelapse');
          console.error('Erreur lors de la suppression du timelapse:', err);
        }
      });
    }
  }
}
