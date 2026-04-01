import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Pipe, PipeTransform } from '@angular/core';

import { SERVER_URL } from '@app/environment';
import { Timelapse } from '@app/interfaces/timelapse';

@Pipe({
  name: 'statusText',
  standalone: true,
})
export class StatusTextPipe implements PipeTransform {
  transform(timelapse: Timelapse): string {
    if (timelapse.ready === undefined) return 'Inconnu';
    return timelapse.ready ? 'Terminé' : 'Enregistrement';
  }
}

@Component({
  selector: 'app-timelapse-library',
  standalone: true,
  imports: [CommonModule, StatusTextPipe],
  templateUrl: './timelapse-library.component.html',
  styleUrl: './timelapse-library.component.css'
})
export class TimelapseLibraryComponent implements OnInit{
  timelapses: Timelapse[] = [];
  error: string | null = null;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.http.get<{
      timelapses: Timelapse[]
    }>(`${SERVER_URL}/timelapse`).subscribe({
      next: (response) => {
        this.timelapses = response.timelapses;
      },
      error: (err) => {
        this.error = `Échec de l'obtention de la liste des timelapses: ${err.error?.detail || err.message}`;
      }
    });
  }

  download(timelapse: Timelapse) {
    window.open(`${SERVER_URL}/timelapse/${timelapse.id}/download`, '_blank');
  }

  delete(timelapse: Timelapse) {
    if (confirm(`Êtes-vous sûr de vouloir supprimer "${timelapse.name}"?`)) {
      this.http.delete(`${SERVER_URL}/timelapse/${timelapse.id}`).subscribe({
        next: () => {
          this.timelapses = this.timelapses.filter(t => t.id !== timelapse.id);
        },
        error: (err) => {
          alert('Échec de la suppression du timelapse');
          console.error('Erreur lors de la suppression du timelapse:', err);
        }
      });
    }
  }
}
