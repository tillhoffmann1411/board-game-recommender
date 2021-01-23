import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';

import { AuthStore } from 'src/app/storemanagement/auth.store';
import { GameStore } from 'src/app/storemanagement/game.store';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {
  isLoggedIn = false;
  route: any;
  enoughRatings = false;

  @Output() public sidenavToggle = new EventEmitter();

  constructor(
    private router: Router,
    private authService: AuthStore,
    private gameStore: GameStore,
  ) { }

  ngOnInit(): void {
    this.route = { url: this.router.url };
    this.router.events.pipe(filter(event => event instanceof NavigationEnd))
      .subscribe((e) => {
        this.route = e;
      });

    this.gameStore.getRatings.subscribe(ratings => {
      this.enoughRatings = ratings.length >= 5;
    });

    this.authService.getIsLoggedIn.subscribe(isloggedIn => {
      this.isLoggedIn = isloggedIn
    });
  }

  public onToggleSidenav() {
    this.sidenavToggle.emit();
  }

  logout() {
    this.authService.signOut();
    this.authService.getIsLoggedIn.subscribe(res => {
      if (!res) {
        this.router.navigate(['/']);
      }
    });
  }

  delete() {
    this.authService.delete();
  }

}
