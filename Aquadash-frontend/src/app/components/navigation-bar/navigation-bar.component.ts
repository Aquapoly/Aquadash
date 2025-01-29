import { Component, inject, OnInit } from '@angular/core';
import { SettingsService } from '@app/services/settings.service';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faBell } from '@fortawesome/free-regular-svg-icons';

@Component({
  selector: 'app-navigation-bar',
  standalone: true,
  imports: [FontAwesomeModule],
  templateUrl: './navigation-bar.component.html',
  styleUrl: './navigation-bar.component.css',
})
export class NavigationBarComponent implements OnInit {
  faBell = faBell;
  darkMode = false;
  private settingsService = inject(SettingsService);

  ngOnInit(): void {
    this.settingsService.applyTheme();
    this.darkMode = this.settingsService.getTheme();
  }
  toggleDarkMode() {
    this.settingsService.toggleDarkMode();
  }
}
