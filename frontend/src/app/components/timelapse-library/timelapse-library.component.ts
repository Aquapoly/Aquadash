import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Pipe, PipeTransform } from '@angular/core';
import { map, Observable } from 'rxjs';

import { SERVER_URL } from '@app/environment';
import { TimelapseMetadata } from '@app/interfaces/timelapse';
import { DurationPipe } from '@app/classes/duration';
import { FileSizePipe } from '@app/classes/filesize';
import { TimelapseStoreService } from '@app/services/timelapse-store.service';
import { TimelapseMetadataDto } from '@app/interfaces/timelapse.dto';
import { mapTimelapseMetadataDto } from '@app/interfaces/timelapse.mapper';
import { TimelapseTabsComponent } from '@app/components/timelapse-tabs/timelapse-tabs.component';
import { TimelapseRecordPanelComponent } from '@app/components/timelapse-record-panel/timelapse-record-panel.component';

@Pipe({
  name: 'timelapseSeconds',
  standalone: true,
})
export class TimelapseSecondsPipe implements PipeTransform {
  transform(timelapse: TimelapseMetadata): number {
    if (!timelapse.start_date) return NaN;
    const start: Date = timelapse.start_date;

    const diffMilli = timelapse.end_date.getTime() - start.getTime();
    return Math.max(0, diffMilli / 1000);
  }
}

@Component({
  selector: 'app-timelapse-library',
  standalone: true,
  imports: [CommonModule, TimelapseSecondsPipe, DurationPipe, TimelapseTabsComponent, FileSizePipe, TimelapseRecordPanelComponent],
  templateUrl: './timelapse-library.component.html',
  styleUrl: './timelapse-library.component.scss'
})
export class TimelapseLibraryComponent implements OnInit{
  readonly SERVER_URL = SERVER_URL;
  readonly timelapses$: Observable<TimelapseMetadata[]>;
  readonly timelapsesEmpty$: Observable<boolean>;
  error: string | null = null;
  viewMode: 'gallery' | 'list' = 'gallery';

  constructor(private http: HttpClient, private store: TimelapseStoreService) {
    this.timelapses$ = this.store.timelapses$.pipe(
      map(timelapses => timelapses.filter(timelapse => timelapse.ready === true)),
    );
    this.timelapsesEmpty$ = this.timelapses$.pipe(
      map(timelapses => timelapses.length === 0),
    );
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

  previewUrl(timelapse: TimelapseMetadata): string {
    const updatedAt = timelapse.latest_frame_date?.getTime() ?? 0;
    return `${SERVER_URL}/timelapse/${timelapse.id}/preview?t=${updatedAt}`;
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
