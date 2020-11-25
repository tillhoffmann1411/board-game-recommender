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
    this.authService.getIsLoggedIn.subscribe(isLoggedIn => {
      this.isLoggedIn = isLoggedIn;
      if (isLoggedIn) {
        this.router.navigate(['/']);
      } else {
        this.router.navigate(['/signin']);
      }
    });
  }

  goToSignin() {
    this.router.navigate(['/signin']);
  }

  goToSignup() {
    this.router.navigate(['/signup']);
  }

  logout() {
    this.authService.signOut();
  }

  delete() {
    this.authService.delete();
  }

}
