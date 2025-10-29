/**
 * Header Component with Navigation
 */

import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Button,
  Box,
} from '@mui/material';
import {
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  Dashboard as DashboardIcon,
  Assignment as TasksIcon,
} from '@mui/icons-material';

interface HeaderProps {
  darkMode: boolean;
  onToggleTheme: () => void;
}

/**
 * Desktop Header with navigation and theme toggle
 */
export const Header = ({ darkMode, onToggleTheme }: HeaderProps) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Задачи', icon: <TasksIcon />, path: '/tasks' },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <AppBar position="static" elevation={2}>
      <Toolbar sx={{ justifyContent: 'space-between', px: 3 }}>
          {/* Left: Logo/Title */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography
              variant="h6"
              component="div"
              sx={{
                fontWeight: 700,
                cursor: 'pointer',
              }}
              onClick={() => navigate('/')}
            >
              Business Planner
            </Typography>
          </Box>

          {/* Center: Navigation */}
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            {menuItems.map((item) => (
              <Button
                key={item.text}
                color="inherit"
                startIcon={item.icon}
                onClick={() => navigate(item.path)}
                sx={{
                  minWidth: 44,
                  minHeight: 44,
                  px: 2,
                  fontWeight: isActive(item.path) ? 600 : 400,
                  borderBottom: isActive(item.path) ? 2 : 0,
                  borderRadius: 0,
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  },
                }}
              >
                {item.text}
              </Button>
            ))}
          </Box>

          {/* Right: Theme Toggle */}
          <IconButton
            color="inherit"
            onClick={onToggleTheme}
            title={darkMode ? 'Светлая тема' : 'Тёмная тема'}
            sx={{ minWidth: 44, minHeight: 44 }}
          >
            {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
          </IconButton>
        </Toolbar>
    </AppBar>
  );
};
