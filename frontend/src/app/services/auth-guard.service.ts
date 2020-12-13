import { Injectable } from '@angular/core';
import { Router, CanActivate } from '@angular/router';

@Injectable()
export class AuthGuard implements CanActivate {

  constructor(
    public router: Router,
  ) { }

  canActivate(): boolean {
    if (localStorage.getItem('isloggedIn') === 'true') {
      return true;
    }
    this.router.navigate(['/signin']);
    return false;
  }
}