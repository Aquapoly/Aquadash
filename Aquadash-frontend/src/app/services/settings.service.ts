import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class SettingsService {
  private darkMode = false;

  constructor() {}

  toggleDarkMode() {
    this.darkMode = !this.darkMode;
    this.applyTheme();
  }

  applyTheme() {
    const theme = this.darkMode ? 'dracula' : 'nord';
    console.log(theme);
    document.body.setAttribute('data-theme', theme);
  }

  getTheme() {
    return this.darkMode;
  }
}
