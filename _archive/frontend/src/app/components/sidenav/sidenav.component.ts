import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { AuthStore } from 'src/app/storemanagement/auth.store';
import { filter } from 'rxjs/operators';
import { GameStore } from 'src/app/storemanagement/game.store';

@Component({
  selector: 'app-sidenav',
  templateUrl: './sidenav.component.html',
  styleUrls: ['./sidenav.component.scss']
})
export class SidenavComponent implements OnInit {
  isLoggedIn = false;
  route: any;
  enoughRatings = false;
  @Output() sidenavClose = new EventEmitter();

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

  public onSidenavClose() {
    this.sidenavClose.emit();
  }

  logout() {
    this.authService.signOut();
    this.authService.getIsLoggedIn.subscribe(res => {
      if (!res) {
        this.router.navigate(['/']);
        this.onSidenavClose();
      }
    });
  }

}
