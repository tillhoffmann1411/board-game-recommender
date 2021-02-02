import { Injectable } from '@angular/core';
import { Action, Selector, State, StateContext, Store } from '@ngxs/store';
import { IRecommenderState } from 'src/app/models/game';
import { GameHttpService } from 'src/app/services/game.service';
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

  constructor(
    private gameService: GameHttpService,
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
    this.gameService.getRecommendedCommonBased().then(res => {
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
    ctx.patchState({ commonBased: recommendedBoardGameIds });
  }

  @Action(Recommender.LoadRecommendationCommonBasedError)
  loadRecommendedBoardGamesError(ctx: StateContext<IRecommenderState>) {
    ctx.setState({ ...ctx.getState(), error: 'Error by loading common based recommended games.' });
  }


  /**
   * Load knn Recommendations
   */
  @Action(Recommender.LoadRecommendationKNN)
  loadRecommendationKNN(ctx: StateContext<IRecommenderState>) {
    this.gameService.getRecommendedKNN().then(res => {
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
    ctx.patchState({ knn: knnIds });
  }

  @Action(Recommender.LoadRecommendationKNNError)
  loadRecommendationKNNError(ctx: StateContext<IRecommenderState>) {
    ctx.setState({ ...ctx.getState(), error: 'Error by loading knn recommended games.' });
  }



  /**
   * Load item based Recommendations
   */
  @Action(Recommender.LoadRecommendationItemBased)
  loadRecommendationItemBased(ctx: StateContext<IRecommenderState>) {
    this.gameService.getRecommendedItemBased().then(res => {
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
    ctx.patchState({ itemBased: recIds });
  }

  @Action(Recommender.LoadRecommendationItemBasedError)
  loadRecommendationItemBasedError(ctx: StateContext<IRecommenderState>) {
    ctx.setState({ ...ctx.getState(), error: 'Error by loading item based recommended games.' });
  }


  /**
   * Load Popularity Recommendations
   */
  @Action(Recommender.LoadRecommendationPopularity)
  loadRecommendationPopularity(ctx: StateContext<IRecommenderState>) {
    this.gameService.getRecommendedPopularity().then(res => {
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
    ctx.patchState({ popularity: recIds });
  }

  @Action(Recommender.LoadRecommendationPopularityError)
  loadRecommendationPopularityError(ctx: StateContext<IRecommenderState>) {
    ctx.setState({ ...ctx.getState(), error: 'Error by loading Popularity recommended games.' });
  }

}