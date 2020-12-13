import { IUser } from './user';

export interface IAuth {
  user: {
    pk: number;
    username: string,
    first_name?: string,
    last_name?: string,
    email?: string,
  },
  token: string,
  non_field_errors?: string[],
}