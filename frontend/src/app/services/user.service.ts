import { environment } from 'src/environments/environment';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { IAuth, IRegisterResponse, ILogoutResponse, IRefreshTokenResponse, ILoginResponse } from '../models/auth';

@Injectable({
  providedIn: 'root'
})
export class UserHttpService {
  baseUrl = environment.api.url;
  headers: HttpHeaders = new HttpHeaders().append('Accept', 'application/json');

  constructor(private http: HttpClient) { }

  login(username: string, password: string): Promise<IRegisterResponse> {
    return this.http.post<IRegisterResponse>(this.baseUrl + '/auth/login/', { username, password }).toPromise();
  }

  register(username: string, password: string, email?: string): Promise<ILoginResponse> {
    const user = {
      username,
      email,
      password1: password,
      password2: password,
    };
    return this.http.post<ILoginResponse>(this.baseUrl + '/auth/register/', user, { headers: this.headers }).toPromise();
  }

  signOut(): Promise<ILogoutResponse> {
    return this.http.post<ILogoutResponse>(this.baseUrl + '/auth/logout/', { headers: this.headers }).toPromise();
  }

  refreshToken(refreshToken: string): Promise<IRefreshTokenResponse> {
    return this.http.post<IRefreshTokenResponse>(this.baseUrl + '/auth/logout/', { headers: this.headers }).toPromise();
  }

  delete(id: number) {
    const params = new HttpParams().append('id', id.toString());
    return this.http.delete<{ detail: string }>(this.baseUrl + '/users', { params, headers: this.headers }).toPromise();
  }
}