export const LIGHT_THEME: string = 'light';
export const DARK_THEME: string = 'dracula';

export const ActuatorTypeToName: { [key: string]: string } = {
  acid_pump: 'Pompe à acide',
  base_pump: 'Pompe à base',
  nutrients_A_pump: 'Pompe à nutriments A',
  nutrients_B_pump: 'Pompe à nutriments B',
};

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
