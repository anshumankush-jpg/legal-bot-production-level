import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { UserContextService } from '../services/user-context.service';

export const SetupGuard: CanActivateFn = (route, state) => {
  const userContext = inject(UserContextService);
  const router = inject(Router);
  
  if (userContext.isSetupComplete()) {
    return true;
  }
  
  router.navigate(['/setup']);
  return false;
};