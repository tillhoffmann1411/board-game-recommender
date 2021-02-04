import { Injectable } from '@angular/core';
import { Action, Selector, State, StateContext, Store } from '@ngxs/store';
import { IRecommenderState } from 'src/app/models/game';
import { RecommendationHttpService } from 'src/app/services/recommendation.service';
import { Recommender } from './recommender.actions';

const DEFAULTS: IRecommenderState = {
  commonBased: [],
  knn: [],
  itemBased: [],
  popularity: [],
  isLoading: false,
  error: ''
}

@State<IRecommenderState>({
  name: 'recommenderState',
  defaults: DEFAULTS
})
@Injectable()
export class RecommenderState {
  loadingCommon = false;
  loadingItem = false;
  loadingPopularity = false;
  loadingKNN = false

  constructor(
    private recommendationService: RecommendationHttpService,
    private store: Store,
  ) { }

  @Selector()
  static getRecommendedBoardGames(state: IRecommenderState) {
    return state;
  }

  @Selector()
  static isLoading(state: IRecommenderState) {
    return state.isLoading;
  }

  /**
   * Load common based Recommendations
   */
  @Action(Recommender.LoadRecommendationCommonBased)
  loadRecommendedBoardGames(ctx: StateContext<IRecommenderState>) {
    this.loadingCommon = true;
    ctx.patchState({ isLoading: this._getIsLoading() });
    this.recommendationService.getRecommendedCommonBased().then(res => {
      if (Array.isArray(res)) {
        this.store.dispatch(new Recommender.LoadRecommendationCommonBasedSuccess(res))
      } else {
        this.store.dispatch(new Recommender.LoadRecommendationCommonBasedError());
      }
    }).catch(() => {
      this.store.dispatch(new Recommender.LoadRecommendationCommonBasedError());
    });
  }

  @Action(Recommender.LoadRecommendationCommonBasedSuccess)
  loadRecommendedBoardGamesSuccess(ctx: StateContext<IRecommenderState>, { recommendedBoardGameIds }: Recommender.LoadRecommendationCommonBasedSuccess) {
    this.loadingCommon = false;
    ctx.patchState({ commonBased: recommendedBoardGameIds, isLoading: this._getIsLoading() });
  }

  @Action(Recommender.LoadRecommendationCommonBasedError)
  loadRecommendedBoardGamesError(ctx: StateContext<IRecommenderState>) {
    this.loadingCommon = false;
    ctx.setState({ ...ctx.getState(), error: 'Error by loading common based recommended games.', isLoading: this._getIsLoading() });
  }


  /**
   * Load knn Recommendations
   */
  @Action(Recommender.LoadRecommendationKNN)
  loadRecommendationKNN(ctx: StateContext<IRecommenderState>) {
    this.loadingKNN = true;
    ctx.patchState({ isLoading: this._getIsLoading() });
    this.recommendationService.getRecommendedKNN().then(res => {
      if (Array.isArray(res)) {
        this.store.dispatch(new Recommender.LoadRecommendationKNNSuccess(res))
      } else {
        this.store.dispatch(new Recommender.LoadRecommendationKNNError());
      }
    }).catch(() => {
      this.store.dispatch(new Recommender.LoadRecommendationKNNError());
    });
  }

  @Action(Recommender.LoadRecommendationKNNSuccess)
  loadRecommendationKNNSuccess(ctx: StateContext<IRecommenderState>, { knnIds }: Recommender.LoadRecommendationKNNSuccess) {
    this.loadingKNN = false;
    ctx.patchState({ knn: knnIds, isLoading: this._getIsLoading() });
  }

  @Action(Recommender.LoadRecommendationKNNError)
  loadRecommendationKNNError(ctx: StateContext<IRecommenderState>) {
    this.loadingKNN = false;
    ctx.setState({ ...ctx.getState(), error: 'Error by loading knn recommended games.', isLoading: this._getIsLoading() });
  }



  /**
   * Load item based Recommendations
   */
  @Action(Recommender.LoadRecommendationItemBased)
  loadRecommendationItemBased(ctx: StateContext<IRecommenderState>) {
    this.loadingItem = true;
    ctx.patchState({ isLoading: this._getIsLoading() });
    this.recommendationService.getRecommendedItemBased().then(res => {
      if (Array.isArray(res)) {
        this.store.dispatch(new Recommender.LoadRecommendationItemBasedSuccess(res))
      } else {
        this.store.dispatch(new Recommender.LoadRecommendationItemBasedError());
      }
    }).catch(() => {
      this.store.dispatch(new Recommender.LoadRecommendationItemBasedError());
    });
  }

  @Action(Recommender.LoadRecommendationItemBasedSuccess)
  loadRecommendationItemBasedSuccess(ctx: StateContext<IRecommenderState>, { recIds }: Recommender.LoadRecommendationItemBasedSuccess) {
    this.loadingItem = false;
    ctx.patchState({ itemBased: recIds, isLoading: this._getIsLoading() });
  }

  @Action(Recommender.LoadRecommendationItemBasedError)
  loadRecommendationItemBasedError(ctx: StateContext<IRecommenderState>) {
    this.loadingItem = false;
    ctx.setState({ ...ctx.getState(), error: 'Error by loading item based recommended games.', isLoading: this._getIsLoading() });
  }


  /**
   * Load Popularity Recommendations
   */
  @Action(Recommender.LoadRecommendationPopularity)
  loadRecommendationPopularity(ctx: StateContext<IRecommenderState>) {
    this.loadingPopularity = true;
    ctx.patchState({ isLoading: this._getIsLoading() });
    this.recommendationService.getRecommendedPopularity().then(res => {
      if (Array.isArray(res)) {
        this.store.dispatch(new Recommender.LoadRecommendationPopularitySuccess(res))
      } else {
        this.store.dispatch(new Recommender.LoadRecommendationPopularityError());
      }
    }).catch(() => {
      this.store.dispatch(new Recommender.LoadRecommendationPopularityError());
    });
  }

  @Action(Recommender.LoadRecommendationPopularitySuccess)
  loadRecommendationPopularitySuccess(ctx: StateContext<IRecommenderState>, { recIds }: Recommender.LoadRecommendationPopularitySuccess) {
    this.loadingPopularity = false;
    ctx.patchState({ popularity: recIds, isLoading: this._getIsLoading() });
  }

  @Action(Recommender.LoadRecommendationPopularityError)
  loadRecommendationPopularityError(ctx: StateContext<IRecommenderState>) {
    this.loadingPopularity = false;
    ctx.setState({ ...ctx.getState(), error: 'Error by loading Popularity recommended games.', isLoading: this._getIsLoading() });
  }

  private _getIsLoading(): boolean {
    return this.loadingCommon || this.loadingItem || this.loadingPopularity || this.loadingKNN;
  }

}