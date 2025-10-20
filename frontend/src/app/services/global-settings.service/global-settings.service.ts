import { Injectable } from '@angular/core';
import {
  ChartThresholdDisplay,
  DARK_THEME,
  LIGHT_THEME,
  LOCAL_STORAGE_KEYS,
  DOM_ATTRIBUTES,
  CSS_CLASSES,
  GLOBAL_SETTINGS_DEFAULTS,
  UNIT_OPTIONS,
} from '@app/constants/constants';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class GlobalSettingsService {
  private darkMode: boolean = GLOBAL_SETTINGS_DEFAULTS.DARK_MODE;
  private thresholdDisplay: ChartThresholdDisplay =
    GLOBAL_SETTINGS_DEFAULTS.THRESHOLD_DISPLAY;
  private temperatureUnit: string = GLOBAL_SETTINGS_DEFAULTS.TEMP_UNIT;
  private ecUnit: string = GLOBAL_SETTINGS_DEFAULTS.EC_UNIT;

  private readonly themeSubject = new BehaviorSubject<string>(
    this.getThemeName()
  );
  private readonly thresholdDisplaySubject =
    new BehaviorSubject<ChartThresholdDisplay>(this.thresholdDisplay);

  private readonly temperatureUnitSubject = new BehaviorSubject<string>(
    this.temperatureUnit
  );

  private readonly ecUnitSubject = new BehaviorSubject<string>(this.ecUnit);

  theme$ = this.themeSubject.asObservable();
  thresholdDisplay$ = this.thresholdDisplaySubject.asObservable();
  temperatureUnit$ = this.temperatureUnitSubject.asObservable();
  ecUnit$ = this.ecUnitSubject.asObservable();

  constructor() {
    this.initializeTheme();
    this.initializeUnits();
  }

  private initializeTheme(): void {
    const savedTheme = localStorage.getItem(LOCAL_STORAGE_KEYS.THEME);
    this.darkMode = savedTheme === DARK_THEME;
    this.applyTheme();
  }

  private initializeUnits(): void {
    const temp = localStorage.getItem(LOCAL_STORAGE_KEYS.TEMP_UNIT);
    const ec = localStorage.getItem(LOCAL_STORAGE_KEYS.EC_UNIT);

    this.temperatureUnit = temp || GLOBAL_SETTINGS_DEFAULTS.TEMP_UNIT;
    this.ecUnit = ec || GLOBAL_SETTINGS_DEFAULTS.EC_UNIT;

    this.temperatureUnitSubject.next(this.temperatureUnit);
    this.ecUnitSubject.next(this.ecUnit);
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

  setTemperatureUnit(unit: string): void {
    this.temperatureUnit = unit;
    localStorage.setItem(LOCAL_STORAGE_KEYS.TEMP_UNIT, unit);
    this.temperatureUnitSubject.next(unit);
  }

  setEcUnit(unit: string): void {
    this.ecUnit = unit;
    localStorage.setItem(LOCAL_STORAGE_KEYS.EC_UNIT, unit);
    this.ecUnitSubject.next(unit);
  }

  getTemperatureUnit(): string {
    return this.temperatureUnit;
  }

  getEcUnit(): string {
    return this.ecUnit;
  }
}
