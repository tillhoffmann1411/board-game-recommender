import { Injectable } from '@angular/core';
import { State, StateContext, Action, Selector, Store } from '@ngxs/store';
import jwt_decode from "jwt-decode";
import { Router } from '@angular/router';

import { Auth } from './auth.actions';
import { UserHttpService } from '../../services/user.service';
import { IUser } from 'src/app/models/user';
import { IAuth } from 'src/app/models/auth';

interface IDecodedToken {
  email: string,
  exp: number,
  user_id: number,
  username: string
}

const DEFAULTS = {
  user: { id: NaN, username: '' },
  error: '',
  loggedIn: false,
  expires: new Date(),
};

export interface IAuthState {
  user: IUser,
  error: string;
  loggedIn: boolean,
  expires: Date,
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
    const expires = this.extractDateFromToken(auth.token);
    const user: IUser = this.extractUserFromAuth(auth);
    localStorage.setItem('isloggedIn', 'true');
    ctx.setState({ user, loggedIn: true, error: '', expires });
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
    const expires = this.extractDateFromToken(auth.token);
    const user = this.extractUserFromAuth(auth);
    localStorage.setItem('isloggedIn', 'true');
    ctx.setState({ user, loggedIn: true, error: '', expires });
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
    } else {
      ctx.setState({ ...DEFAULTS, error: 'Error by logging out: ' + response.detail });
    }
    localStorage.clear();
  }


  /**
   * Delete
   */

  @Action(Auth.Delete)
  async delete(ctx: StateContext<IAuthState>) {
    const response = await this.userService.delete(ctx.getState().user.id);
    if (response.detail) {
      ctx.setState(DEFAULTS);
    } else {
      ctx.setState({ ...ctx.getState(), error: 'Deleting user failed: ' + response.detail });
    }
    localStorage.clear();
  }

  private extractDateFromToken(token: string): Date {
    const decodedToken: IDecodedToken = jwt_decode(token);
    return new Date((new Date(0)).setUTCSeconds(decodedToken.exp));
  }

  private extractUserFromAuth(auth: IAuth): IUser {
    return {
      id: auth.user.pk,
      username: auth.user.username,
      email: auth.user.email,
      firstName: auth.user.first_name,
      lastName: auth.user.last_name
    };
  }
}