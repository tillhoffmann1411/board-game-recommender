import { IBoardGame, IRecResponse, IRating, IOnlineGame } from 'src/app/models/game';

export namespace Game {
  export class getBoardGames {
    static readonly type = '[Game] Get Board Games'
  }

  export class getBoardGame {
    static readonly type = '[Game] Get Board Game'
  }

  export class getRecommendedBoardGames {
    static readonly type = '[Game] Get recommended Board Games'
  }

  export class getRatings {
    static readonly type = '[Game] Get Ratings'
  }



  /**
   * Send User Ratings
   */
  export class SendRating {
    static readonly type = '[Game] Send user rating';
    constructor(public rating: IRating) { }
  }

  export class SendRatingError {
    static readonly type = '[Game] Failed to send user rating';
    constructor() { }
  }

  export class SendRatingSuccess {
    static readonly type = '[Game] Successful sended user rating';
    constructor(public rating: IRating) { }
  }

  /**
   * Load User Ratings
   */
  export class LoadRatings {
    static readonly type = '[Game] Load user ratings';
    constructor() { }
  }

  export class LoadRatingsError {
    static readonly type = '[Game] Failed to load user ratings';
    constructor() { }
  }

  export class LoadRatingsSuccess {
    static readonly type = '[Game] Successful loaded user ratings';
    constructor(public ratings: IRating[]) { }
  }



  /**
   * Load Board Games
   */
  export class LoadBoardGames {
    static readonly type = '[Game] Load Board Games';
    constructor() { }
  }

  export class LoadBoardGamesError {
    static readonly type = '[Game] Failed to load Board Games';
    constructor() { }
  }

  export class LoadBoardGamesSuccess {
    static readonly type = '[Game] Successful loaded Board Games';
    constructor(public boardGames: IBoardGame[]) { }
  }

  /**
   * Load Board Games
   */
  export class LoadBoardGame {
    static readonly type = '[Game] Load single Board Game';
    constructor(public boardGameId: number) { }
  }

  export class LoadBoardGameError {
    static readonly type = '[Game] Failed to load single Board Game';
    constructor() { }
  }

  export class LoadBoardGameSuccess {
    static readonly type = '[Game] Successful loaded single Board Game';
    constructor(public boardGame: IBoardGame) { }
  }

  /**
 * Load Generics
 */
  export class LoadCategories {
    static readonly type = '[Game] Load categories';
    constructor() { }
  }
  export class LoadMechanics {
    static readonly type = '[Game] Load mechanics';
    constructor() { }
  }
  export class LoadAuthors {
    static readonly type = '[Game] Load authors';
    constructor() { }
  }
  export class LoadPublishers {
    static readonly type = '[Game] Load publishers';
    constructor() { }
  }

  export class LoadGenericError {
    static readonly type = '[Game] Failed to load generic';
    constructor(public kind: 'categories' | 'mechanics' | 'authors' | 'publishers') { }
  }

  export class LoadGenericSuccess {
    static readonly type = '[Game] Successful loaded generic';
    constructor(public res: any[], public kind: 'categories' | 'mechanics' | 'authors' | 'publishers') { }
  }
}
