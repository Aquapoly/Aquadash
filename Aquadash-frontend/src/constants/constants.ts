export const LIGHT_THEME: string = 'light';
export const DARK_THEME: string = 'dracula';

interface colors {
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
}

export const THEME_COLOR: { [key in string]: colors } = {
  [DARK_THEME]: {
    colorScheme: 'dark',
    primary: '#1DB88E',
    secondary: '#3ac26c',
    accent: '#ffb86c',
    neutral: '#414558',
    base100: '#282a36',
    baseContent: '#f8f8f2',
    info: '#8be9fd',
    success: '#50fa7b',
    warning: '#f1fa8c',
    error: '#ff5555',
    infoContent: '#071316',
    lineColor: '#ccdef7',
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
    success: '#00a96e',
    warning: '#ffbf00',
    error: '#ff6368',
    infoContent: '#042e49',
    lineColor: '#4571af',
  },
};
