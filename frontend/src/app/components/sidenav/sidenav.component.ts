import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { AuthStore } from 'src/app/storemanagement/auth.store';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-sidenav',
  templateUrl: './sidenav.component.html',
  styleUrls: ['./sidenav.component.scss']
})
export class SidenavComponent implements OnInit {
  isLoggedIn = false;
  route: any;
  @Output() sidenavClose = new EventEmitter();

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


  public onSidenavClose() {
    this.sidenavClose.emit();
  }
}
