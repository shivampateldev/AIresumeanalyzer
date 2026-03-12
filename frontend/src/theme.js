import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // blue
    },
    secondary: {
      main: '#90caf9', // light blue
    },
    background: {
      default: '#f0f7ff',
      paper: '#ffffff',
    },
    text: {
      primary: '#0d1a26',
    },
  },
});

export default theme;
