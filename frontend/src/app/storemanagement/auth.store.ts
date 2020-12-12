import { Store, Select } from '@ngxs/store';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Auth } from './state/auth.actions';
import { AuthState, IAuthState } from './state/auth.state';
import { IUser } from '../models/user';

@Injectable({
  providedIn: 'root'
})
export class AuthStore {

  constructor(private store: Store) { }

  @Select(AuthState.getIsLoggedIn)
  public getIsLoggedIn: Observable<boolean>;

  @Select(AuthState.getError)
  public getError: Observable<string>;

  getUserSnapshot(): IUser {
    return this.store.selectSnapshot<IAuthState>(state => state).user;
  }

  signIn(username: string, password: string): Observable<void> {
    return this.store.dispatch(new Auth.SignIn(username, password));
  }

  signUp(username: string, password: string, email?: string, firstName?: string, lastName?: string) {
    return this.store.dispatch(new Auth.SignUp(username, password, email, firstName, lastName));
  }

  signOut(): Observable<void> {
    return this.store.dispatch(new Auth.SignOut());
  }

  delete() {
    return this.store.dispatch(new Auth.Delete());
  }
}