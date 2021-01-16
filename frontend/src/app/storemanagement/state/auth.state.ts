import { Injectable } from '@angular/core';
import { State, StateContext, Action, Selector, Store } from '@ngxs/store';
import jwt_decode from "jwt-decode";

import { Auth } from './auth.actions';
import { UserHttpService } from '../../services/user.service';
import { IUser } from 'src/app/models/user';

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
    if (localStorage.getItem('isloggedIn') === 'true') {
      return true;
    } else {
      return false
    }
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

  @Action(Auth.Login)
  login(ctx: StateContext<IAuthState>, { username, password }: Auth.Login) {
    this.userService.login(username, password).then(res => {
      if (res.access_token) {
        this.store.dispatch(new Auth.LoginSuccess({ user: res.user, jwt: res.access_token }));
      } else {
        this.store.dispatch(new Auth.LoginError());
      }
    }).catch(() => {
      this.store.dispatch(new Auth.LoginError());
    });
  }

  @Action(Auth.LoginSuccess)
  loginSuccess(ctx: StateContext<IAuthState>, { auth }: Auth.LoginSuccess) {
    const expires = this.extractDateFromToken(auth.jwt);
    const user: IUser = auth.user;
    localStorage.setItem('isloggedIn', 'true');
    ctx.setState({ user, loggedIn: true, error: '', expires });
  }

  @Action(Auth.LoginError)
  loginError(ctx: StateContext<IAuthState>) {
    ctx.setState({ ...DEFAULTS, error: 'Sign in failed' });
  }


  /**
   * Sign up
   */

  @Action(Auth.Register)
  register(ctx: StateContext<IAuthState>, { username, password, email }: Auth.Register) {
    this.userService.register(username, password, email).then(res => {
      if (res.access_token) {
        this.store.dispatch(new Auth.RegisterSuccess({ user: res.user, jwt: res.access_token }));
      } else {
        this.store.dispatch(new Auth.RegisterError());
      }
    }).catch(() => {
      this.store.dispatch(new Auth.RegisterError());
    });
  }

  @Action(Auth.RegisterSuccess)
  registerSuccess(ctx: StateContext<IAuthState>, { auth }: Auth.RegisterSuccess) {
    const expires = this.extractDateFromToken(auth.jwt);
    const user = auth.user;
    localStorage.setItem('isloggedIn', 'true');
    ctx.setState({ user, loggedIn: true, error: '', expires });
  }

  @Action(Auth.RegisterError)
  registerError(ctx: StateContext<IAuthState>, { auth }: Auth.RegisterSuccess) {
    ctx.setState({ ...DEFAULTS, error: 'Sign up failed' });
  }


  /**
   * Sign out
   */

  @Action(Auth.SignOut)
  async signOut(ctx: StateContext<IAuthState>) {
    try {
      const response = await this.userService.signOut();
    } catch (e) { }
    localStorage.clear();
    ctx.setState(DEFAULTS);
  }


  /**
   * Delete
   */

  @Action(Auth.Delete)
  async delete(ctx: StateContext<IAuthState>) {
    try {
      const response = await this.userService.delete(ctx.getState().user.id);
    } catch (e) { }
    localStorage.clear();
    ctx.setState(DEFAULTS);
  }

  private extractDateFromToken(token: string): Date {
    const decodedToken: IDecodedToken = jwt_decode(token);
    return new Date((new Date(0)).setUTCSeconds(decodedToken.exp));
  }
}