import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthStore } from './storemanagement/auth.store';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'board-game-recommender';
  isLoggedIn = false;

  constructor(
    private router: Router,
    private authService: AuthStore
  ) { }

  ngOnInit() {
    this.authService.getIsLoggedIn.subscribe(isloggedIn => {
      this.isLoggedIn = isloggedIn
    });
  }
}
