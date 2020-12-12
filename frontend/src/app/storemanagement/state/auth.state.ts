import { Injectable } from '@angular/core';
import { State, StateContext, Action, Selector, Store } from '@ngxs/store';

import { IAuth } from '../../models/auth';
import { Auth } from './auth.actions';
import { UserHttpService } from '../../services/user.service';

const DEFAULTS = {
  user: { id: '', username: '' },
  error: '',
  loggedIn: false,
  jwtExpires: 0,
  refreshToken: '',
  refreshTokenExpires: 0,
};

export interface IAuthState extends IAuth {
  error: string;
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
      if (res.loggedIn) {
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
    ctx.setState({ ...auth, error: '' });
  }

  @Action(Auth.SignInError)
  signInError(ctx: StateContext<IAuthState>, { auth }: Auth.SignInSuccess) {
    ctx.setState({ ...DEFAULTS, error: 'Sign in failed' });
  }


  /**
   * Sign up
   */

  @Action(Auth.SignUp)
  signUp(ctx: StateContext<IAuthState>, { username, password, email, firstName, lastName }: Auth.SignUp) {
    this.userService.signUp(username, password, email, firstName, lastName).then(res => {
      if (res.loggedIn) {
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
    ctx.setState({ ...auth, error: '' });
  }

  @Action(Auth.SignUpError)
  signUpError(ctx: StateContext<IAuthState>, { auth }: Auth.SignUpSuccess) {
    ctx.setState({ ...DEFAULTS, error: 'Sign up failed' });
  }


  /**
   * Sign out
   */

  @Action(Auth.SignOut)
  async signOut(ctx: StateContext<IAuthState>) {
    const response = await this.userService.signOut();
    if (response.success) {
      ctx.setState(DEFAULTS);
    }
  }


  /**
   * Delete
   */

  @Action(Auth.Delete)
  async delete(ctx: StateContext<IAuthState>) {
    const response = await this.userService.delete(ctx.getState().user.id);
    if (response.success) {
      ctx.setState(DEFAULTS);
    } else {
      ctx.patchState({ error: 'Deleting user failed' });
    }
  }
}