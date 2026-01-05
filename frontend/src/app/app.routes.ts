import { Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';
import { SetupGuard } from './guards/setup.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/login',
    pathMatch: 'full'
  },
  {
    path: 'login',
    loadComponent: () => import('./pages/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'setup',
    loadComponent: () => import('./pages/setup/setup-wizard.component').then(m => m.SetupWizardComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'chat',
    loadComponent: () => import('./pages/chat/chat.component').then(m => m.ChatComponent),
    canActivate: [AuthGuard, SetupGuard]
  },
  {
    path: 'profile',
    loadComponent: () => import('./pages/profile/profile.component').then(m => m.ProfileComponent),
    canActivate: [AuthGuard]
  },
  // Legacy routes (optional - keep for backward compatibility)
  {
    path: 'documents',
    loadComponent: () => import('./components/documents/documents.component').then(m => m.DocumentsComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'analytics',
    loadComponent: () => import('./components/analytics/analytics.component').then(m => m.AnalyticsComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'upload',
    loadComponent: () => import('./components/upload/upload.component').then(m => m.UploadComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'evaluation',
    loadComponent: () => import('./components/evaluation/evaluation.component').then(m => m.EvaluationComponent),
    canActivate: [AuthGuard]
  },
  {
    path: '**',
    redirectTo: '/login'
  }
];

