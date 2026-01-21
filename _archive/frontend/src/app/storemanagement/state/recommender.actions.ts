import { IRecResponse } from 'src/app/models/game';

export namespace Recommender {
  /**
   * Load recommended Board Games
   */
  export class LoadRecommendationCommonBased {
    static readonly type = '[Game] Load common based recommended Board Games';
    constructor() { }
  }

  export class LoadRecommendationCommonBasedError {
    static readonly type = '[Game] Failed to load common based  recommended Board Games';
    constructor() { }
  }

  export class LoadRecommendationCommonBasedSuccess {
    static readonly type = '[Game] Successful loaded common based  recommended Board Games';
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

  /**
   * Load recommended popularity
   */
  export class LoadRecommendationPopularity {
    static readonly type = '[Game] Load recommended Popularity Board Games';
    constructor() { }
  }

  export class LoadRecommendationPopularityError {
    static readonly type = '[Game] Failed to load Popularity recommended Board Games';
    constructor() { }
  }

  export class LoadRecommendationPopularitySuccess {
    static readonly type = '[Game] Successful loaded Popularity recommended Board Games';
    constructor(public recIds: IRecResponse[]) { }
  }


}
