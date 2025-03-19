import { Injectable } from '@angular/core';
import { DARK_THEME, LIGHT_THEME } from '../../../constants/constants';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class GlobalSettingsService {
  private darkMode = false;

  private themeSubject = new BehaviorSubject<string>(this.getThemeName());
  theme$ = this.themeSubject.asObservable();

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
    document.documentElement.setAttribute(
      'class',
      this.getTheme() ? 'dark' : 'light'
    );
    this.themeSubject.next(this.getThemeName());
  }

  getTheme(): boolean {
    return this.darkMode;
  }

  getThemeName(): string {
    return this.darkMode ? DARK_THEME : LIGHT_THEME;
  }
}
