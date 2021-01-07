import { IAuth } from 'src/app/models/auth';

export namespace Auth {

  export class getIsLoggedIn {
    static readonly type = '[Auth] Get Logged in status'
  }

  export class getError {
    static readonly type = '[Auth] Get Error'
  }


  /**
   * Sign up
   */

  export class Login {
    static readonly type = '[Auth] Sign in and set data';
    constructor(public username: string, public password: string) { }
  }

  export class LoginError {
    static readonly type = '[Auth] Failed to Sign in';
    constructor() { }
  }

  export class LoginSuccess {
    static readonly type = '[Auth] Successful Signed in';
    constructor(public auth: IAuth) { }
  }


  /**
   * Sign up
   */

  export class Register {
    static readonly type = '[Auth] Sign up and set data';
    constructor(public username: string, public password: string, public email?: string, public firstName?: string, public lastName?: string) { }
  }

  export class RegisterError {
    static readonly type = '[Auth] Failed to Sign up';
    constructor() { }
  }

  export class RegisterSuccess {
    static readonly type = '[Auth] Successful Signed up';
    constructor(public auth: IAuth) { }
  }


  /**
   * Sign uot
   */

  export class SignOut {
    static readonly type = '[Auth] Logout';
    constructor() { }
  }


  /**
   * Delete
   */

  export class Delete {
    static readonly type = '[Auth] Delete User';
    constructor() { }
  }
}