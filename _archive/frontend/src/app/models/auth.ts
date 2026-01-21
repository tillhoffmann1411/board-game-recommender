import { IUser } from './user';

export interface IAuth {
  user: IUser,
  jwt: string,
}

// API Responses
export interface IRegisterResponse {
  accessToken: string,
  refreshToken: string,
  user: IUser
}

export interface ILoginResponse {
  accessToken: string,
  refreshToken: string,
  user: IUser
}

export interface ILogoutResponse {
  detail: string
}

export interface IRefreshTokenResponse {
  access: string
}