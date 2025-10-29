/**
 * Main App Component with Routing and Theme
 */

import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { createAppTheme } from './theme';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { BusinessTasks } from './pages/BusinessTasks';

function App() {
  const [darkMode, setDarkMode] = useState(false);

  // Use centralized theme from src/theme/index.ts
  const theme = createAppTheme(darkMode ? 'dark' : 'light');

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          {/* Header with Navigation */}
          <Header darkMode={darkMode} onToggleTheme={() => setDarkMode(!darkMode)} />

          {/* Main Content */}
          <Box component="main" sx={{ flexGrow: 1, width: '100%' }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/business/:businessId" element={<BusinessTasks />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
