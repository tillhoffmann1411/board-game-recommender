import { environment } from 'src/environments/environment';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { IAuth } from '../models/auth';

@Injectable({
  providedIn: 'root'
})
export class UserHttpService {
  baseUrl = environment.api.url;

  constructor(private http: HttpClient) { }

  signIn(email: string, password: string) {
    return this.http.post<IAuth>(this.baseUrl + '/users/signin', { email, password }, { withCredentials: true }).toPromise();
  }

  signUp(name: string, email: string, password: string) {
    return this.http.post<IAuth>(this.baseUrl + '/users/signup', { name, email, password }, { withCredentials: true }).toPromise();
  }

  signOut() {
    return this.http.get<{ success: boolean }>(this.baseUrl + '/users/signout', { withCredentials: true }).toPromise();
  }

  delete(id: string) {
    const params = new HttpParams().append('id', id);
    return this.http.delete<{ success: boolean }>(this.baseUrl + '/users', { withCredentials: true, params }).toPromise();
  }
}