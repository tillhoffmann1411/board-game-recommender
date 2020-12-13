import { Injectable } from '@angular/core';
import { State, StateContext, Action, Selector, Store } from '@ngxs/store';

import { IAuth } from '../../models/auth';
import { Auth } from './auth.actions';
import { UserHttpService } from '../../services/user.service';
import { IUser } from 'src/app/models/user';
import { Router } from '@angular/router';

const DEFAULTS = {
  user: { id: NaN, username: '' },
  error: '',
  loggedIn: false,
};

export interface IAuthState {
  user: IUser,
  error: string;
  loggedIn: boolean,
}

@State<IAuthState>({
  name: 'auth',
  defaults: DEFAULTS
})
@Injectable()
export class AuthState {

  constructor(
    private userService: UserHttpService,
    private store: Store,
    private router: Router
  ) { }

  @Selector()
  static getIsLoggedIn(state: IAuthState) {
    return state.loggedIn;
  }

  @Selector()
  static getError(state: IAuthState) {
    return state.error;
  }

  @Selector()
  static getMe(state: IAuthState) {
    return state.user;
  }


  /**
   * Sign in
   */

  @Action(Auth.SignIn)
  signIn(ctx: StateContext<IAuthState>, { username, password }: Auth.SignIn) {
    this.userService.signIn(username, password).then(res => {
      console.log(res);
      if (res.token) {
        this.store.dispatch(new Auth.SignInSuccess(res));
      } else {
        this.store.dispatch(new Auth.SignInError());
      }
    }).catch(() => {
      this.store.dispatch(new Auth.SignInError());
    });
  }

  @Action(Auth.SignInSuccess)
  signInSuccess(ctx: StateContext<IAuthState>, { auth }: Auth.SignInSuccess) {
    const user: IUser = {
      id: auth.user.pk,
      username: auth.user.username,
      email: auth.user.email,
      firstName: auth.user.first_name,
      lastName: auth.user.last_name
    }
    ctx.setState({ user, loggedIn: true, error: '' });
  }

  @Action(Auth.SignInError)
  signInError(ctx: StateContext<IAuthState>, { auth }: Auth.SignInSuccess) {
    ctx.setState({ ...DEFAULTS, error: auth.non_field_errors ? auth.non_field_errors.toString() : 'Sign in failed' });
  }


  /**
   * Sign up
   */

  @Action(Auth.SignUp)
  signUp(ctx: StateContext<IAuthState>, { username, password, email, firstName, lastName }: Auth.SignUp) {
    this.userService.signUp(username, password, email, firstName, lastName).then(res => {
      if (res.token) {
        this.store.dispatch(new Auth.SignUpSuccess(res));
      } else {
        this.store.dispatch(new Auth.SignUpError());
      }
    }).catch(() => {
      this.store.dispatch(new Auth.SignUpError());
    });
  }

  @Action(Auth.SignUpSuccess)
  signUpSuccess(ctx: StateContext<IAuthState>, { auth }: Auth.SignUpSuccess) {
    const user: IUser = {
      id: auth.user.pk,
      username: auth.user.username,
      email: auth.user.email,
      firstName: auth.user.first_name,
      lastName: auth.user.last_name
    }
    ctx.setState({ user, loggedIn: true, error: '' });
  }

  @Action(Auth.SignUpError)
  signUpError(ctx: StateContext<IAuthState>, { auth }: Auth.SignUpSuccess) {
    ctx.setState({ ...DEFAULTS, error: auth.non_field_errors ? auth.non_field_errors.toString() : 'Sign up failed' });
  }


  /**
   * Sign out
   */

  @Action(Auth.SignOut)
  async signOut(ctx: StateContext<IAuthState>) {
    const response = await this.userService.signOut();
    if (response.detail === 'Successfully logged out.') {
      ctx.setState(DEFAULTS);
      this.router.navigate(['/']);
    } else {
      ctx.setState({ ...DEFAULTS, error: 'Error by logging out: ' + response.detail });
    }
  }


  /**
   * Delete
   */

  @Action(Auth.Delete)
  async delete(ctx: StateContext<IAuthState>) {
    const response = await this.userService.delete(ctx.getState().user.id);
    if (response.detail) {
      ctx.setState(DEFAULTS);
      this.router.navigate(['/']);
    } else {
      ctx.setState({ ...ctx.getState(), error: 'Deleting user failed: ' + response.detail });
    }
  }
}