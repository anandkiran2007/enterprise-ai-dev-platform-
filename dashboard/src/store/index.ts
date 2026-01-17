import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      login: (token, user) =>
        set(
          { token, user, isAuthenticated: true, isLoading: false },
          false,
          'auth/login'
        ),
      logout: () =>
        set(
          { user: null, token: null, isAuthenticated: false, isLoading: false },
          false,
          'auth/logout'
        ),
      setLoading: (isLoading) =>
        set({ isLoading }, false, 'auth/setLoading'),
    }),
    { name: 'auth-store' }
  )
);

interface Project {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'building' | 'failed' | 'completed';
  repository: string;
  lastBuild?: string;
  buildTime?: number;
  coverage?: number;
}

interface ProjectState {
  projects: Project[];
  selectedProject: Project | null;
  isLoading: boolean;
  setProjects: (projects: Project[]) => void;
  setSelectedProject: (project: Project | null) => void;
  addProject: (project: Project) => void;
  updateProject: (id: string, updates: Partial<Project>) => void;
  removeProject: (id: string) => void;
  setLoading: (loading: boolean) => void;
}

export const useProjectStore = create<ProjectState>()(
  devtools(
    (set, get) => ({
      projects: [],
      selectedProject: null,
      isLoading: false,
      setProjects: (projects) =>
        set({ projects, isLoading: false }, false, 'project/setProjects'),
      setSelectedProject: (project) =>
        set({ selectedProject: project }, false, 'project/setSelectedProject'),
      addProject: (project) =>
        set(
          (state) => ({
            projects: [...state.projects, project],
          }),
          false,
          'project/addProject'
        ),
      updateProject: (id, updates) =>
        set(
          (state) => ({
            projects: state.projects.map((p) =>
              p.id === id ? { ...p, ...updates } : p
            ),
            selectedProject:
              state.selectedProject?.id === id
                ? { ...state.selectedProject, ...updates }
                : state.selectedProject,
          }),
          false,
          'project/updateProject'
        ),
      removeProject: (id) =>
        set(
          (state) => ({
            projects: state.projects.filter((p) => p.id !== id),
            selectedProject:
              state.selectedProject?.id === id ? null : state.selectedProject,
          }),
          false,
          'project/removeProject'
        ),
      setLoading: (isLoading) =>
        set({ isLoading }, false, 'project/setLoading'),
    }),
    { name: 'project-store' }
  )
);
