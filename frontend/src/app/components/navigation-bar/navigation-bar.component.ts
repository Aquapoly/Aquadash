import { Component, inject, OnInit } from '@angular/core';
import { GlobalSettingsService } from '@app/services/global-settings.service/global-settings.service';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faBell } from '@fortawesome/free-regular-svg-icons';

@Component({
  selector: 'app-navigation-bar',
  imports: [FontAwesomeModule],
  templateUrl: './navigation-bar.component.html',
  styleUrl: './navigation-bar.component.scss',
})
export class NavigationBarComponent implements OnInit {
  faBell = faBell;
  darkMode = false;
  private readonly settingsService = inject(GlobalSettingsService);

  ngOnInit(): void {
    this.settingsService.applyTheme();
    this.darkMode = this.settingsService.getTheme();
  }
  toggleDarkMode(): void {
    this.settingsService.toggleDarkMode();
    this.darkMode = this.settingsService.getTheme();
  }
}
