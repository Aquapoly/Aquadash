import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { Subscription } from 'rxjs';
import { GlobalSettingsService } from '@app/services/global-settings.service/global-settings.service';
import { ApiService } from '@app/services/api.service';
import { LIGHT_THEME, THEME_COLOR } from '@app/constants/constants';

@Component({
  selector: 'app-export-button',
  standalone: true,
  imports: [FontAwesomeModule, CommonModule, HttpClientModule],
  templateUrl: './export-button.component.html',
  styleUrl: './export-button.component.scss',
})
export class ExportButtonComponent implements OnInit, OnDestroy {
  public readonly THEME_COLOR = THEME_COLOR;

  theme: string = LIGHT_THEME;
  private themeSubscription?: Subscription;

  constructor(
    private readonly globalSettings: GlobalSettingsService,
    private readonly apiService: ApiService
  ) {}

  ngOnInit(): void {
    this.theme = this.globalSettings.getThemeName();
    this.themeSubscription = this.globalSettings.theme$.subscribe((theme) => {
      this.theme = theme;
    });
  }

  ngOnDestroy(): void {
    if (this.themeSubscription) {
      this.themeSubscription.unsubscribe();
    }
  }

  onClick() {
    this.apiService.exportMeasurements().subscribe({
      next: (response) => {
        const blob = response.body;
        const url = window.URL.createObjectURL(blob!);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'all_sensors_measurements.csv';
        link.click();
        window.URL.revokeObjectURL(url);
      },
      error: (err) => {
        console.error('Erreur lors de l\'export des données', err);
      },
    });
  }
}
