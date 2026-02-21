import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

interface Timelapse {
  id: string;
  date: string;
  frames: number;
  name: string;
}

@Component({
  selector: 'app-timelapse-library',
  imports: [CommonModule],
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
    }>('http://localhost:8000/timelapses').subscribe({
      next: (response) => {
        this.timelapses = response.timelapses;
      },
      error: (err) => {
        this.error = 'Échec de l\'obtention de la liste des timelapses: ' + (err.error?.detail || err.message);
      }
    });
  }

  download(timelapse: Timelapse) {
    window.open(`http://localhost:8000/timelapse/${timelapse.id}/download`, '_blank');
  }

  delete(timelapse: Timelapse) {
    if (confirm(`Êtes-vous sûr de vouloir supprimer "${timelapse.name}"?`)) {
      this.http.delete(`http://localhost:8000/timelapse/${timelapse.id}`).subscribe({
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
