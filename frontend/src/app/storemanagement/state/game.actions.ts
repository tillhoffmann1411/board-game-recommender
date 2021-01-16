import { IBoardGame, IGameState, IRating } from 'src/app/models/game';

export namespace Game {
  export class getBoardGames {
    static readonly type = '[Game] Get Board Games'
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
  export class SendRatings {
    static readonly type = '[Game] Send user ratings';
    constructor(public rating: IRating) { }
  }

  export class SendRatingsError {
    static readonly type = '[Game] Failed to send user ratings';
    constructor() { }
  }

  export class SendRatingsSuccess {
    static readonly type = '[Game] Successful sended user ratings';
    constructor(public rating: IRating) { }
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
   * Load recommended Board Games
   */
  export class LoadRecommendedBoardGames {
    static readonly type = '[Game] Load recommended Board Games';
    constructor() { }
  }

  export class LoadRecommendedBoardGamesError {
    static readonly type = '[Game] Failed to load recommended Board Games';
    constructor() { }
  }

  export class LoadRecommendedBoardGamesSuccess {
    static readonly type = '[Game] Successful loaded recommended Board Games';
    constructor(public recommendedBoardGames: IBoardGame[]) { }
  }
}