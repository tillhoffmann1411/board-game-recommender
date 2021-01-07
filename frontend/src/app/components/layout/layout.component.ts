import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { AuthStore } from 'src/app/storemanagement/auth.store';

@Component({
  selector: 'app-layout',
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.scss']
})
export class LayoutComponent implements OnInit {
  isLoggedIn = false;

  constructor(
    private router: Router,
    private authService: AuthStore
  ) { }

  ngOnInit(): void {
    this.authService.getIsLoggedIn.subscribe(isloggedIn => {
      this.isLoggedIn = isloggedIn
      if (this.isLoggedIn) {
        this.router.navigate(['/profile']);
      } else {
        this.router.navigate(['/login']);
      }
    });
  }

  goToHome() {
    this.router.navigate(['/']);
  }

  goToSignin() {
    this.router.navigate(['/login']);
  }

  goToSignup() {
    this.router.navigate(['/register']);
  }

  logout() {
    this.authService.signOut();
    this.authService.getIsLoggedIn.subscribe(res => {
      console.log('Logout:', res);
      if (!res) {
        this.router.navigate(['/']);
      }
    });
  }

  delete() {
    this.authService.delete();
  }

}
