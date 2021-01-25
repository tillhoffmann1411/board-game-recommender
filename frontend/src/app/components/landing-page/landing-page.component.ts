import { Component, OnInit } from '@angular/core';
import { AuthStore } from 'src/app/storemanagement/auth.store';

@Component({
  selector: 'app-landing-page',
  templateUrl: './landing-page.component.html',
  styleUrls: ['./landing-page.component.scss']
})
export class LandingPageComponent implements OnInit {
  isLoggedIn = false;

  constructor(
    private authService: AuthStore
  ) { }

  ngOnInit(): void {
    this.authService.getIsLoggedIn.subscribe(isloggedIn => {
      this.isLoggedIn = isloggedIn
    });
  }
}
