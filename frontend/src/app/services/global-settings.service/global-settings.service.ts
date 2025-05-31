import { Injectable } from '@angular/core';
import {
  ChartThresholdDisplay,
  DARK_THEME,
  LIGHT_THEME,
  LOCAL_STORAGE_KEYS,
  DOM_ATTRIBUTES,
  CSS_CLASSES,
  GLOBAL_SETTINGS_DEFAULTS,
} from '@app/constants/constants';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class GlobalSettingsService {
  private darkMode: boolean = GLOBAL_SETTINGS_DEFAULTS.DARK_MODE;
  private thresholdDisplay: ChartThresholdDisplay =
    GLOBAL_SETTINGS_DEFAULTS.THRESHOLD_DISPLAY;

  private readonly themeSubject = new BehaviorSubject<string>(
    this.getThemeName()
  );
  private readonly thresholdDisplaySubject =
    new BehaviorSubject<ChartThresholdDisplay>(this.thresholdDisplay);

  theme$ = this.themeSubject.asObservable();
  thresholdDisplay$ = this.thresholdDisplaySubject.asObservable();

  constructor() {
    this.initializeTheme();
  }

  private initializeTheme(): void {
    const savedTheme = localStorage.getItem(LOCAL_STORAGE_KEYS.THEME);
    this.darkMode = savedTheme === DARK_THEME;
    this.applyTheme();
  }

  setThresholdDisplay(display: ChartThresholdDisplay): void {
    this.thresholdDisplay = display;
    this.thresholdDisplaySubject.next(display);
  }

  toggleDarkMode(): void {
    this.darkMode = !this.darkMode;
    this.saveAndApplyTheme();
  }

  private saveAndApplyTheme(): void {
    this.applyTheme();
    localStorage.setItem(LOCAL_STORAGE_KEYS.THEME, this.getThemeName());
  }

  applyTheme(): void {
    const themeName = this.getThemeName();
    const cssClass = this.darkMode ? CSS_CLASSES.DARK : CSS_CLASSES.LIGHT;

    document.documentElement.setAttribute(DOM_ATTRIBUTES.DATA_THEME, themeName);
    document.documentElement.setAttribute(DOM_ATTRIBUTES.CLASS, cssClass);

    this.themeSubject.next(themeName);
  }

  getTheme(): boolean {
    return this.darkMode;
  }

  getThemeName(): string {
    return this.darkMode ? DARK_THEME : LIGHT_THEME;
  }
}
