import { environment } from 'src/environments/environment';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { IAuth } from '../models/auth';

@Injectable({
  providedIn: 'root'
})
export class UserHttpService {
  baseUrl = environment.api.url;
  headers: HttpHeaders = new HttpHeaders().append('Accept', 'application/json');

  constructor(private http: HttpClient) { }

  signIn(username: string, password: string) {
    return this.http.post<IAuth>(this.baseUrl + '/auth/login/', { username, password }).toPromise();
  }

  signUp(username: string, password: string, email?: string, firstName?: string, lastName?: string) {
    const user = {
      username,
      email,
      password1: password,
      password2: password,
      last_name: lastName,
      first_name: firstName
    };
    return this.http.post<IAuth>(this.baseUrl + '/auth/registration/', user, { headers: this.headers }).toPromise();
  }

  signOut() {
    return this.http.get<{ success: boolean }>(this.baseUrl + '/auth/logout/', { headers: this.headers }).toPromise();
  }

  delete(id: number) {
    const params = new HttpParams().append('id', id.toString());
    return this.http.delete<{ success: boolean }>(this.baseUrl + '/users', { params, headers: this.headers }).toPromise();
  }
}