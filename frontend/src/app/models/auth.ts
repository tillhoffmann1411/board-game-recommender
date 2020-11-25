import { IUser } from './user';

export interface IAuth {
  user: IUser,
  loggedIn: boolean,
  jwtExpires: number;
  refreshToken: string;
  refreshTokenExpires: number;
}