import { Injectable } from '@angular/core';
import { DARK_THEME, LIGHT_THEME } from '../../../constants/constants';

@Injectable({
  providedIn: 'root',
})
export class GlobalSettingsService {
  private darkMode = false;

  constructor() {
    const savedTheme = localStorage.getItem('theme');
    this.darkMode = savedTheme === DARK_THEME;
    this.applyTheme();
  }

  toggleDarkMode(): void {
    this.darkMode = !this.darkMode;
    this.applyTheme();
    localStorage.setItem('theme', this.getThemeName());
  }

  applyTheme(): void {
    document.documentElement.setAttribute('data-theme', this.getThemeName());
  }

  getTheme(): boolean {
    return this.darkMode;
  }

  private getThemeName(): string {
    return this.darkMode ? DARK_THEME : LIGHT_THEME;
  }
}
