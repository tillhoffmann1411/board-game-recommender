import { IBoardGame, IRecResponse, IRating } from 'src/app/models/game';

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
    constructor(public recommendedBoardGameIds: IRecResponse[]) { }
  }

  /**
   * Load recommended Board Games
   */
  export class LoadRecommendationKNN {
    static readonly type = '[Game] Load recommended KNN Board Games';
    constructor() { }
  }

  export class LoadRecommendationKNNError {
    static readonly type = '[Game] Failed to load KNN recommended Board Games';
    constructor() { }
  }

  export class LoadRecommendationKNNSuccess {
    static readonly type = '[Game] Successful loaded KNN recommended Board Games';
    constructor(public knnIds: IRecResponse[]) { }
  }


  /**
   * Load recommended Board Games
   */
  export class LoadRecommendationItemBased {
    static readonly type = '[Game] Load recommended ItemBased Board Games';
    constructor() { }
  }

  export class LoadRecommendationItemBasedError {
    static readonly type = '[Game] Failed to load ItemBased recommended Board Games';
    constructor() { }
  }

  export class LoadRecommendationItemBasedSuccess {
    static readonly type = '[Game] Successful loaded ItemBased recommended Board Games';
    constructor(public recIds: IRecResponse[]) { }
  }


}
