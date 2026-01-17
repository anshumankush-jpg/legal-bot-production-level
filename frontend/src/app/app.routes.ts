import { Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';
import { SetupGuard } from './guards/setup.guard';
import { ProvisionedGuard } from './guards/provisioned.guard';
import { RoleGuard } from './guards/role.guard';

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
    path: 'not-provisioned',
    loadComponent: () => import('./pages/not-provisioned/not-provisioned.component').then(m => m.NotProvisionedComponent)
  },
  {
    path: 'access-denied',
    loadComponent: () => import('./pages/access-denied/access-denied.component').then(m => m.AccessDeniedComponent)
  },
  {
    path: 'setup',
    loadComponent: () => import('./pages/setup/setup-wizard.component').then(m => m.SetupWizardComponent),
    canActivate: [AuthGuard, ProvisionedGuard]
  },
  {
    path: 'chat',
    loadComponent: () => import('./pages/chat/chat.component').then(m => m.ChatComponent),
    canActivate: [AuthGuard, ProvisionedGuard, SetupGuard]
  },
  // New ChatGPT-style app shell
  {
    path: 'app',
    loadComponent: () => import('./components/app-shell/app-shell.component').then(m => m.AppShellComponent),
    children: [
      {
        path: '',
        redirectTo: 'chat',
        pathMatch: 'full'
      },
      {
        path: 'chat',
        loadComponent: () => import('./pages/chat-page/chat-page.component').then(m => m.ChatPageComponent)
      },
      {
        path: 'chat/:id',
        loadComponent: () => import('./pages/chat-page/chat-page.component').then(m => m.ChatPageComponent)
      },
      {
        path: 'personalization',
        loadComponent: () => import('./pages/personalization/personalization.component').then(m => m.PersonalizationComponent)
      },
      {
        path: 'settings',
        loadComponent: () => import('./pages/settings/settings.component').then(m => m.SettingsComponent)
      }
    ]
  },
  {
    path: 'profile',
    loadComponent: () => import('./pages/profile/profile.component').then(m => m.ProfileComponent),
    canActivate: [AuthGuard, ProvisionedGuard]
  },
  // Personalization page
  {
    path: 'personalization',
    loadComponent: () => import('./pages/personalization/personalization.component').then(m => m.PersonalizationComponent),
    canActivate: [AuthGuard, ProvisionedGuard]
  },
  // Settings page
  {
    path: 'settings',
    loadComponent: () => import('./pages/settings/settings.component').then(m => m.SettingsComponent),
    canActivate: [AuthGuard, ProvisionedGuard]
  },
  // Help pages
  {
    path: 'help',
    loadComponent: () => import('./pages/help/help.component').then(m => m.HelpComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'help/:section',
    loadComponent: () => import('./pages/help/help.component').then(m => m.HelpComponent),
    canActivate: [AuthGuard]
  },
  // Static policy pages (public)
  {
    path: 'terms',
    loadComponent: () => import('./pages/static/terms.component').then(m => m.TermsComponent)
  },
  {
    path: 'privacy',
    loadComponent: () => import('./pages/static/privacy.component').then(m => m.PrivacyComponent)
  },
  {
    path: 'cookies',
    loadComponent: () => import('./pages/static/cookies.component').then(m => m.CookiesComponent)
  },
  // Legacy routes (optional - keep for backward compatibility)
  {
    path: 'documents',
    loadComponent: () => import('./components/documents/documents.component').then(m => m.DocumentsComponent),
    canActivate: [AuthGuard, ProvisionedGuard]
  },
  {
    path: 'analytics',
    loadComponent: () => import('./components/analytics/analytics.component').then(m => m.AnalyticsComponent),
    canActivate: [AuthGuard, ProvisionedGuard]
  },
  {
    path: 'upload',
    loadComponent: () => import('./components/upload/upload.component').then(m => m.UploadComponent),
    canActivate: [AuthGuard, ProvisionedGuard]
  },
  {
    path: 'evaluation',
    loadComponent: () => import('./components/evaluation/evaluation.component').then(m => m.EvaluationComponent),
    canActivate: [AuthGuard, ProvisionedGuard]
  },
  // Lawyer-only routes
  {
    path: 'lawyer',
    children: [
      {
        path: 'dashboard',
        loadComponent: () => import('./pages/lawyer/lawyer-dashboard.component').then(m => m.LawyerDashboardComponent),
        canActivate: [AuthGuard, ProvisionedGuard, RoleGuard],
        data: { requireApprovedLawyer: true }
      }
    ]
  },
  {
    path: '**',
    redirectTo: '/login'
  }
];

