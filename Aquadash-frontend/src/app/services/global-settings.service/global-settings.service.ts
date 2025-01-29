import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class GlobalSettingsService {
  private darkMode = false;

  constructor() {
    const savedTheme = localStorage.getItem('theme');
    this.darkMode = savedTheme === 'dracula';
    this.applyTheme();
  }

  toggleDarkMode() {
    this.darkMode = !this.darkMode;
    this.applyTheme();
    localStorage.setItem('theme', this.darkMode ? 'dracula' : 'nord');
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
