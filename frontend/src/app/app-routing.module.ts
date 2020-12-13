import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { LandingPageComponent } from './components/landing-page/landing-page.component';

import { AuthGuard } from './services/auth-guard.service';

import { LayoutComponent } from './components/layout/layout.component';
import { SignInComponent } from './components/sign-in/sign-in.component';
import { SignUpComponent } from './components/sign-up/sign-up.component';
import { UserModule } from './user/user.module';

const routes: Routes = [
  {
    path: '', component: LayoutComponent, children: [
      { path: '', component: LandingPageComponent },
      { path: 'signin', component: SignInComponent },
      { path: 'signup', component: SignUpComponent },
      { path: 'profile', canActivate: [AuthGuard], loadChildren: () => UserModule },
    ]
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
