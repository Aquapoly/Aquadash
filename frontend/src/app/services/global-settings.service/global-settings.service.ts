import { Injectable } from '@angular/core';
import {
  ChartThresholdDisplay,
  DARK_THEME,
  LIGHT_THEME,
  LOCAL_STORAGE_KEYS,
  DOM_ATTRIBUTES,
  CSS_CLASSES,
  GLOBAL_SETTINGS_DEFAULTS,
  SENSOR_UNIT_STORAGE_KEYS,
} from '@app/constants/constants';
import { BehaviorSubject } from 'rxjs';
import { SensorType } from '@app/interfaces/sensor-type';

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

  private readonly sensorUnitsSubject = new BehaviorSubject<
    Record<string, string>
  >({});

  theme$ = this.themeSubject.asObservable();
  thresholdDisplay$ = this.thresholdDisplaySubject.asObservable();
  sensorUnits$ = this.sensorUnitsSubject.asObservable();

  constructor() {
    this.initializeTheme();
    const units = this.loadInitialUnits();
    this.sensorUnitsSubject.next(units);
  }

  private initializeTheme(): void {
    const savedTheme = localStorage.getItem(LOCAL_STORAGE_KEYS.THEME);
    const savedThresholdDisplay = localStorage.getItem(
      LOCAL_STORAGE_KEYS.THRESHOLDDISPLAY
    );
    this.darkMode = savedTheme === DARK_THEME;
    if (savedThresholdDisplay != null) {
      this.setThresholdDisplay(
        Number(savedThresholdDisplay) as ChartThresholdDisplay
      );
    }
    this.applyTheme();
  }

  private loadInitialUnits(): Record<string, string> {
    const units: Record<string, string> = {};
    for (const [type, key] of Object.entries(SENSOR_UNIT_STORAGE_KEYS)) {
      const saved = localStorage.getItem(key);
      if (saved) units[type] = saved;
    }
    return units;
  }

  setThresholdDisplay(display: ChartThresholdDisplay): void {
    this.thresholdDisplay = display;
    this.thresholdDisplaySubject.next(display);
    this.saveThresholdTheme();
  }

  toggleDarkMode(): void {
    this.darkMode = !this.darkMode;
    this.saveAndApplyTheme();
  }

  private saveAndApplyTheme(): void {
    this.applyTheme();
    localStorage.setItem(LOCAL_STORAGE_KEYS.THEME, this.getThemeName());
  }

  private saveThresholdTheme(): void {
    localStorage.setItem(
      LOCAL_STORAGE_KEYS.THRESHOLDDISPLAY,
      this.getThresholdDisplay().toLocaleString()
    );
  }

  applyTheme(): void {
    const themeName = this.getThemeName();
    const cssClass = this.darkMode ? CSS_CLASSES.DARK : CSS_CLASSES.LIGHT;

    document.documentElement.setAttribute(DOM_ATTRIBUTES.DATA_THEME, themeName);
    document.documentElement.setAttribute(DOM_ATTRIBUTES.CLASS, cssClass);

    this.themeSubject.next(themeName);
  }

  getThresholdDisplay(): ChartThresholdDisplay {
    return this.thresholdDisplay;
  }

  getTheme(): boolean {
    return this.darkMode;
  }

  getThemeName(): string {
    return this.darkMode ? DARK_THEME : LIGHT_THEME;
  }

  getSensorUnit(sensorType: SensorType): string | null {
    const key = SENSOR_UNIT_STORAGE_KEYS[sensorType];
    return key ? localStorage.getItem(key) : null;
  }

  setSensorUnit(sensorType: SensorType, unit: string): void {
    const key = SENSOR_UNIT_STORAGE_KEYS[sensorType];
    if (key) {
      localStorage.setItem(key, unit);

      const current = this.sensorUnitsSubject.value;
      this.sensorUnitsSubject.next({
        ...current,
        [sensorType]: unit,
      });
    }
  }
}
