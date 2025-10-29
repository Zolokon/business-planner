/**
 * Dashboard Page - Overview of all 4 businesses
 */

import { useEffect, useState } from 'react';
import {
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Box,
  CircularProgress,
  Chip,
} from '@mui/material';
import {
  Build as BuildIcon,
  Science as ScienceIcon,
  Lightbulb as LightbulbIcon,
  LocalShipping as LocalShippingIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { getTasks } from '../api/tasks';
import { BUSINESSES } from '../types';

const BUSINESS_ICONS: Record<number, React.ReactNode> = {
  1: <BuildIcon fontSize="large" />,
  2: <ScienceIcon fontSize="large" />,
  3: <LightbulbIcon fontSize="large" />,
  4: <LocalShippingIcon fontSize="large" />,
};

interface BusinessStats {
  total: number;
  high_priority: number;
  in_progress: number;
  overdue: number;
}

export const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<Record<number, BusinessStats>>({});

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Load tasks for each business
      const statsPromises = BUSINESSES.map(async (business) => {
        const tasks = await getTasks({ business_id: business.id });

        // Filter active tasks (not done)
        const activeTasks = tasks.filter((t) => t.status !== 'done');

        const stats: BusinessStats = {
          total: activeTasks.length,
          high_priority: activeTasks.filter((t) => t.priority === 1).length,
          in_progress: activeTasks.filter((t) => t.status === 'in_progress').length,
          overdue: activeTasks.filter((t) => {
            if (!t.deadline) return false;
            return new Date(t.deadline) < new Date();
          }).length,
        };

        return [business.id, stats] as [number, BusinessStats];
      });

      const statsArray = await Promise.all(statsPromises);
      const statsObject = Object.fromEntries(statsArray);
      setStats(statsObject);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="80vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ px: 3, py: 4 }}>
      {/* Header Section */}
      <Box sx={{ mb: 6, mt: 2 }}>
        <Typography
          variant="h3"
          component="h1"
          gutterBottom
          fontWeight={700}
        >
          Бизнес Панель
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Управление задачами для 4 бизнесов
        </Typography>
      </Box>

      {/* Business Cards Grid */}
      <Grid container spacing={3}>
        {BUSINESSES.map((business) => {
          const businessStats = stats[business.id] || {
            total: 0,
            high_priority: 0,
            in_progress: 0,
            overdue: 0,
          };

          return (
            <Grid size={{ xs: 12, sm: 6, md: 3 }} key={business.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  borderTop: `4px solid ${business.color}`,
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4,
                  },
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box display="flex" alignItems="center" mb={3}>
                    <Box
                      sx={{
                        bgcolor: `${business.color}20`,
                        color: business.color,
                        borderRadius: 2,
                        p: 1,
                        mr: 2,
                      }}
                    >
                      {BUSINESS_ICONS[business.id]}
                    </Box>
                    <Box>
                      <Typography variant="h5" component="h2">
                        {business.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {business.description}
                      </Typography>
                    </Box>
                  </Box>

                  <Box mt={3}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2" color="text.secondary">
                        Всего задач
                      </Typography>
                      <Typography variant="h6">{businessStats.total}</Typography>
                    </Box>

                    <Box display="flex" gap={1} flexWrap="wrap" mt={2}>
                      {businessStats.high_priority > 0 && (
                        <Chip
                          label={`${businessStats.high_priority} срочных`}
                          color="error"
                          size="small"
                        />
                      )}
                      {businessStats.in_progress > 0 && (
                        <Chip
                          label={`${businessStats.in_progress} в работе`}
                          color="info"
                          size="small"
                        />
                      )}
                      {businessStats.overdue > 0 && (
                        <Chip
                          label={`${businessStats.overdue} просрочено`}
                          color="warning"
                          size="small"
                        />
                      )}
                    </Box>
                  </Box>
                </CardContent>

                <CardActions>
                  <Button
                    fullWidth
                    variant="contained"
                    sx={{
                      bgcolor: business.color,
                      '&:hover': {
                        bgcolor: business.color,
                        opacity: 0.9,
                      },
                    }}
                    onClick={() => navigate(`/business/${business.id}`)}
                  >
                    Открыть задачи
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
};
