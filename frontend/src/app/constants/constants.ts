import { SensorType } from '@app/interfaces/sensor-type';

export const LIGHT_THEME: string = 'light';
export const DARK_THEME: string = 'dracula';

export const WHOLE_GAUGE_ROTATION_OFFSET: number = 45;

export const LIMIT = 100;

export const ActuatorTypeToName: { [key: string]: string } = {
  acid_pump: 'Pompe à acide',
  base_pump: 'Pompe à base',
  nutrients_A_pump: 'Pompe à nutriments A',
  nutrients_B_pump: 'Pompe à nutriments B',
};

export enum ThresholdNames {
  CriticallyLow = 'Critically low',
  CriticallyHigh = 'Critically high',
  Low = 'Low',
  High = 'High',
  Normal = 'Normal',
}

export enum ThresholdsBackgroundOpacity {
  Critical = '20',
  Normal = '10',
}

interface Colors {
  colorScheme: string;
  primary: string;
  secondary: string;
  accent: string;
  neutral: string;
  base100: string;
  baseContent: string;
  info: string;
  success: string;
  warning: string;
  error: string;
  infoContent: string;
  lineColor: string;
  danger: string;
}

export const THEME_COLOR: { [key in string]: Colors } = {
  [DARK_THEME]: {
    colorScheme: 'dark',
    primary: '#1DB88E',
    secondary: '#3ac26c',
    accent: '#ffb86c',
    neutral: '#414558',
    base100: '#282a36',
    baseContent: '#f8f8f2',
    info: '#8be9fd',
    success: '#60cc96',
    warning: '#f1fa8c',
    error: '#ff5555',
    infoContent: '#071316',
    lineColor: '#d3edff',
    danger: '#ff5555',
  },
  [LIGHT_THEME]: {
    colorScheme: 'light',
    primary: '#65c3c8',
    secondary: '#66cc8a',
    accent: '#00d3be',
    neutral: '#2B3440',
    base100: '#ffffff',
    baseContent: '#1f2937',
    info: '#00b5fb',
    success: '#00a992',
    warning: '#ffbf00',
    error: '#ff6368',
    infoContent: '#042e49',
    lineColor: '#0067cd',
    danger: '#ff5555',
  },
};

export enum ChartThresholdDisplay {
  NoThreshold,
  ColoredLine,
  ColoredBackground,
  ColoredBackgroundWithLine,
}

export const CHART_CHOICES: { [key in ChartThresholdDisplay]: string } = {
  [ChartThresholdDisplay.NoThreshold]: 'Pas de seuil',
  [ChartThresholdDisplay.ColoredLine]: 'Seuils colorés sur la ligne',
  [ChartThresholdDisplay.ColoredBackground]: 'Seuils colorés sur le fond',
  [ChartThresholdDisplay.ColoredBackgroundWithLine]:
    'Seuils colorés sur la ligne et le fond',
};

export const MODAL_MESSAGES = {
  SUCCESS_TITLE: 'Succès',
  SUCCESS_CONTENT: 'Les paramètres ont été mis à jour avec succès.',
  SUCCESS_CONTENT_ADDED: 'Nouveau actuateur ajouté avec succès.',
  ERROR_TITLE: 'Erreur',
  ERROR_CONTENT:
    'Une erreur est survenue lors de la mise à jour des paramètres.',
  ERROR_CONTENT_ADDED: 'Une erreur est survenue lors de l\'ajout du nouveau actuateur.',
} as const;

export const API_DEFAULTS = {
  ACTUATORS_PAGE: 0,
} as const;

export const TIPPY_CONFIG = {
  placement: 'top' as const,
  animation: 'scale-subtle' as const,
  theme: 'light' as const,
  arrow: true,
} as const;

export enum SortDirection {
  ASC = 'asc',
  DESC = 'desc',
}

export const STATUS_PAGE_DEFAULTS = {
  COLUMN_COUNT: 2,
  CHART_SIZE_INITIAL: 100,
  CHART_SIZE_DIVISOR: 78,
  NO_DATA_MESSAGE: 'No data',
} as const;

export const SENSOR_VALIDITY_CLASSES = {
  NEUTRAL: 'neutral-content',
  ERROR: 'error',
  WARNING: 'warning',
  SUCCESS: 'success',
} as const;

export const LOCAL_STORAGE_KEYS = {
  THEME: 'theme',
  THRESHOLDDISPLAY: 'thresholdDisplay',
  SENSOR_ORDER: 'sensor_order'
} as const;

export const DOM_ATTRIBUTES = {
  DATA_THEME: 'data-theme',
  CLASS: 'class',
} as const;

export const CSS_CLASSES = {
  DARK: 'dark',
  LIGHT: 'light',
} as const;

export const GLOBAL_SETTINGS_DEFAULTS = {
  DARK_MODE: false,
  THRESHOLD_DISPLAY: ChartThresholdDisplay.ColoredBackgroundWithLine,
} as const;

export const SENSOR_SERVICE_DEFAULTS = {
  PROTOTYPE_ID: 0,
  DEFAULT_RANGE_INDEX: 3,
  PADDING_LENGTH: 2,
  PADDING_CHAR: '0',
} as const;

export const TIME_RANGE_OPTIONS = [
  {
    name: 'Dernière heure',
    value: { days: 0, hours: 1, minutes: 0, seconds: 0 },
  },
  {
    name: 'Dernières 24h',
    value: { days: 1, hours: 0, minutes: 0, seconds: 0 },
  },
  {
    name: 'Dernière semaine',
    value: { days: 7, hours: 0, minutes: 0, seconds: 0 },
  },
  {
    name: 'Dernière année',
    value: { days: 365, hours: 0, minutes: 0, seconds: 0 },
  },
] as const;

export const SENSOR_TYPE_TITLES = {
  [SensorType.ec]: 'EC',
  [SensorType.ph]: 'pH',
  [SensorType.temperature]: 'Température',
  [SensorType.humidity]: 'Humidité',
  [SensorType.water_level]: "Niveau d'eau",
  [SensorType.boolean_water_level]: "Niveau d'eau",
  [SensorType.oxygen]: 'Oxygène',
} as const;

export const API_ENDPOINTS = {
  MEASUREMENTS: 'measurements',
  SENSORS: 'sensors',
  LAST: 'last',
} as const;
