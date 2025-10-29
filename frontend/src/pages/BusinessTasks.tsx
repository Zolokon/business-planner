/**
 * Business Tasks Page - List of tasks for a specific business
 */

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography,
  Box,
  Button,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  CheckCircle as CheckCircleIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { getTasks, deleteTask, completeTask } from '../api/tasks';
import { Task, BUSINESSES, PRIORITY_LABELS, PRIORITY_COLORS, STATUS_LABELS } from '../types';

export const BusinessTasks = () => {
  const { businessId } = useParams<{ businessId: string }>();
  const navigate = useNavigate();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('');

  const business = BUSINESSES.find((b) => b.id === Number(businessId));

  useEffect(() => {
    if (businessId) {
      loadTasks();
    }
  }, [businessId]);

  const loadTasks = async () => {
    setLoading(true);
    try {
      const data = await getTasks({ business_id: Number(businessId) });
      setTasks(data);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteTask = async (taskId: number) => {
    try {
      await completeTask(taskId, 60); // Default 60 minutes
      loadTasks();
    } catch (error) {
      console.error('Failed to complete task:', error);
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    if (confirm('Вы уверены, что хотите удалить задачу?')) {
      try {
        await deleteTask(taskId);
        loadTasks();
      } catch (error) {
        console.error('Failed to delete task:', error);
      }
    }
  };

  const formatDeadline = (deadline: string | null | undefined) => {
    if (!deadline) return '—';
    const date = new Date(deadline);
    const now = new Date();
    const isOverdue = date < now;

    return (
      <Chip
        label={date.toLocaleDateString('ru-RU')}
        color={isOverdue ? 'error' : 'default'}
        size="small"
      />
    );
  };

  const filteredTasks = tasks.filter((task) => {
    if (statusFilter && task.status !== statusFilter) return false;
    if (priorityFilter && task.priority !== Number(priorityFilter)) return false;
    return true;
  });

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

  if (!business) {
    return (
      <Box sx={{ px: 3, py: 4 }}>
        <Typography>Бизнес не найден</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ px: 3, py: 4 }}>
      <Box display="flex" alignItems="center" mb={4}>
        <IconButton onClick={() => navigate('/')} sx={{ mr: 2 }}>
          <ArrowBackIcon />
        </IconButton>
        <Box flexGrow={1}>
          <Typography variant="h3" component="h1" fontWeight={700}>
            {business.name}
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mt: 1 }}>
            {business.description}
          </Typography>
        </Box>
        <Chip
          label={`${filteredTasks.length} задач`}
          sx={{ bgcolor: business.color, color: 'white' }}
        />
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box display="flex" gap={2} flexWrap="wrap">
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Статус</InputLabel>
            <Select
              value={statusFilter}
              label="Статус"
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <MenuItem value="">Все</MenuItem>
              <MenuItem value="open">Открыта</MenuItem>
              <MenuItem value="in_progress">В работе</MenuItem>
              <MenuItem value="done">Завершена</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Приоритет</InputLabel>
            <Select
              value={priorityFilter}
              label="Приоритет"
              onChange={(e) => setPriorityFilter(e.target.value)}
            >
              <MenuItem value="">Все</MenuItem>
              <MenuItem value="1">Высокий</MenuItem>
              <MenuItem value="2">Средний</MenuItem>
              <MenuItem value="3">Низкий</MenuItem>
              <MenuItem value="4">Отложено</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="outlined"
            onClick={() => {
              setStatusFilter('');
              setPriorityFilter('');
            }}
          >
            Сбросить фильтры
          </Button>
        </Box>
      </Paper>

      {/* Tasks Table */}
      <TableContainer component={Paper} sx={{ overflowX: 'auto' }}>
        <Table sx={{ minWidth: 650 }}>
          <TableHead>
            <TableRow sx={{ bgcolor: business.color + '20' }}>
              <TableCell>Задача</TableCell>
              <TableCell>Приоритет</TableCell>
              <TableCell>Статус</TableCell>
              <TableCell>Дедлайн</TableCell>
              <TableCell>Исполнитель</TableCell>
              <TableCell align="right">Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredTasks.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography color="text.secondary" py={4}>
                    Нет задач
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              filteredTasks.map((task) => (
                <TableRow key={task.id} hover>
                  <TableCell>
                    <Typography variant="body1">{task.title}</Typography>
                    {task.description && (
                      <Typography variant="body2" color="text.secondary">
                        {task.description}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={PRIORITY_LABELS[task.priority]}
                      size="small"
                      sx={{
                        bgcolor: PRIORITY_COLORS[task.priority],
                        color: 'white',
                      }}
                    />
                  </TableCell>
                  <TableCell>{STATUS_LABELS[task.status]}</TableCell>
                  <TableCell>{formatDeadline(task.deadline)}</TableCell>
                  <TableCell>{task.assigned_to || '—'}</TableCell>
                  <TableCell align="right">
                    {task.status !== 'done' && (
                      <IconButton
                        color="success"
                        onClick={() => handleCompleteTask(task.id)}
                        title="Завершить"
                      >
                        <CheckCircleIcon />
                      </IconButton>
                    )}
                    <IconButton
                      color="error"
                      onClick={() => handleDeleteTask(task.id)}
                      title="Удалить"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};
