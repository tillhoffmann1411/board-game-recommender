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

  signIn(email: string, password: string): Observable<void> {
    return this.store.dispatch(new Auth.SignIn(email, password));
  }

  signUp(name: string, email: string, password: string) {
    return this.store.dispatch(new Auth.SignUp(name, email, password));
  }

  signOut(): Observable<void> {
    return this.store.dispatch(new Auth.SignOut());
  }

  delete() {
    return this.store.dispatch(new Auth.Delete());
  }
}