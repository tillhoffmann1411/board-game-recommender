import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';

import { AuthStore } from 'src/app/storemanagement/auth.store';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {
  isLoggedIn = false;
  route: any;

  @Output() public sidenavToggle = new EventEmitter();

  constructor(
    private router: Router,
    private authService: AuthStore
  ) { }

  ngOnInit(): void {
    this.route = { url: this.router.url };
    this.router.events.pipe(filter(event => event instanceof NavigationEnd))
      .subscribe((e) => {
        this.route = e;
      });

    this.authService.getIsLoggedIn.subscribe(isloggedIn => {
      this.isLoggedIn = isloggedIn
      if (this.isLoggedIn) {
        this.router.navigate(['/profile']);
      }
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
