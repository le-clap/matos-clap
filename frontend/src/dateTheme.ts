import { createTheme } from '@mui/material/styles';

export const dateTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: 'rgb(var(--color-ink-900))',
      // light: 'rgb(var(--color-brand-50))',
      // dark: 'rgb(var(--color-ink-900))',
      contrastText: 'var(--color-primary-strong)',
    },
    background: {
      default: 'var(--color-bg)',
      // paper: 'var(--color-ink-50)',
    },
    text: {
      primary: 'rgb(var(--color-content))',
      secondary: 'var(--color-content-muted)',
    },
    divider: 'var(--color-border-strong)',
  },
  typography: {
    fontFamily: 'var(--font-sans, "Inter", sans-serif)',
  },
  components: {
    // Example: Forcing the DatePicker paper to use your CSS variables
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: 'var(--color-bg)',
          accentColor: 'var(--color-primary)',
          color: 'var(--color-content)',
        },
      },
    },
  },
});
