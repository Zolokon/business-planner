/**
 * TypeScript types for Business Planner
 */

export interface Task {
  id: number;
  user_id: number;
  business_id: number;
  project_id?: number | null;
  title: string;
  description?: string | null;
  status: 'open' | 'in_progress' | 'done';
  priority: 1 | 2 | 3 | 4; // 1=High, 2=Medium, 3=Low, 4=Backlog
  estimated_duration?: number | null;
  actual_duration?: number | null;
  deadline?: string | null;
  assigned_to?: string | null;
  created_at: string;
  updated_at: string;
  completed_at?: string | null;
}

export interface Business {
  id: number;
  name: string;
  color: string;
  icon: string;
  description: string;
}

export const BUSINESSES: Business[] = [
  {
    id: 1,
    name: 'INVENTUM',
    color: '#f44336',
    icon: 'Build',
    description: 'Ремонт стоматологического оборудования',
  },
  {
    id: 2,
    name: 'INVENTUM LAB',
    color: '#2196f3',
    icon: 'Science',
    description: 'Зуботехническая лаборатория (CAD/CAM)',
  },
  {
    id: 3,
    name: 'R&D',
    color: '#4caf50',
    icon: 'Lightbulb',
    description: 'Разработка прототипов',
  },
  {
    id: 4,
    name: 'TRADE',
    color: '#ff9800',
    icon: 'LocalShipping',
    description: 'Импорт из Китая',
  },
];

export const PRIORITY_LABELS: Record<number, string> = {
  1: 'Высокий',
  2: 'Средний',
  3: 'Низкий',
  4: 'Отложено',
};

export const PRIORITY_COLORS: Record<number, string> = {
  1: '#f44336',
  2: '#ff9800',
  3: '#4caf50',
  4: '#9e9e9e',
};

export const STATUS_LABELS: Record<string, string> = {
  open: 'Открыта',
  in_progress: 'В работе',
  done: 'Завершена',
};
