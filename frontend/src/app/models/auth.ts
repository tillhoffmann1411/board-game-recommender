import { IUser } from './user';

export interface IAuth {
  user: IUser,
  jwt: string,
}

// API Responses
export interface IRegisterResponse {
  access_token: string,
  refresh_token: string,
  user: IUser
}

export interface ILoginResponse {
  access_token: string,
  refresh_token: string,
  user: IUser
}

export interface ILogoutResponse {
  detail: string
}

export interface IRefreshTokenResponse {
  access: string
}