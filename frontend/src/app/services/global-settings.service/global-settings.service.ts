import { Injectable } from '@angular/core';
import { Sensor } from '@app/interfaces/sensor';
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
  private sensorOrder : string[] =  []; 
  

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
    const savedThresholdDisplay = localStorage.getItem(LOCAL_STORAGE_KEYS.THRESHOLDDISPLAY);

    this.darkMode = savedTheme === DARK_THEME;
    if (savedThresholdDisplay != null) {
      this.setThresholdDisplay(Number(savedThresholdDisplay) as ChartThresholdDisplay);
    }
    this.applyTheme();
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

  getSensorOrder(): string[]{
    const order = localStorage.getItem(LOCAL_STORAGE_KEYS.SENSOR_ORDER);
    this.sensorOrder = order !== null ? JSON.parse(order) : [];
    return this.sensorOrder;
  }

  saveSensorOrder(sensors: string[]):void{
    localStorage.setItem(LOCAL_STORAGE_KEYS.SENSOR_ORDER, JSON.stringify(sensors) );
  }

  private saveAndApplyTheme(): void {
    this.applyTheme();
    localStorage.setItem(LOCAL_STORAGE_KEYS.THEME, this.getThemeName());
  }
  
  private saveThresholdTheme() : void {
    localStorage.setItem(LOCAL_STORAGE_KEYS.THRESHOLDDISPLAY, this.getThresholdDisplay().toLocaleString());
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
}
