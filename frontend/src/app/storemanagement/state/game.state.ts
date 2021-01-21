import { Injectable } from '@angular/core';
import { Action, Selector, State, StateContext, Store } from '@ngxs/store';
import { IGameState, IRating } from 'src/app/models/game';
import { GameHttpService } from 'src/app/services/game.service';
import { Game } from './game.actions';

const DEFAULTS: IGameState = {
  boardGames: [],
  recommendedBoardGames: [],
  ratings: [],
  error: ''
}

@State<IGameState>({
  name: 'gameState',
  defaults: DEFAULTS
})
@Injectable()
export class GameState {

  constructor(
    private gameService: GameHttpService,
    private store: Store,
  ) { }

  @Selector()
  static getBoardGames(state: IGameState) {
    return state.boardGames;
  }

  @Selector()
  static getRecommendedBoardGames(state: IGameState) {
    return state.recommendedBoardGames;
  }

  @Selector()
  static getRatings(state: IGameState) {
    return state.ratings;
  }




  /**
   * send Ratings
   */
  @Action(Game.SendRating)
  sendRating(ctx: StateContext<IGameState>, { rating }: Game.SendRating) {
    this.gameService.sendRatings(rating).then(res => {
      if (res) {
        this.store.dispatch(new Game.SendRatingSuccess(rating))
      } else {
        this.store.dispatch(new Game.SendRatingError());
      }
    }).catch(() => {
      this.store.dispatch(new Game.SendRatingError());
    });
  }

  @Action(Game.SendRatingSuccess)
  sendRatingSuccess(ctx: StateContext<IGameState>, { rating }: Game.SendRatingSuccess) {
    const oldRatings = new Map<number, number>();

    ctx.getState().ratings.forEach(rating => {
      oldRatings.set(rating.game, rating.rating);
    });
    oldRatings.set(rating.game, rating.rating);

    const newRatings: IRating[] = [];
    oldRatings.forEach((rating, game) => {
      newRatings.push({ game, rating });
    });
    ctx.setState({ ...ctx.getState(), ratings: newRatings });
  }

  @Action(Game.SendRatingError)
  sendRatingError(ctx: StateContext<IGameState>) {
    ctx.setState({ ...ctx.getState(), error: 'Error by sending ratings.' });
  }


  /**
 * load Ratings
 */
  @Action(Game.LoadRatings)
  loadRating(ctx: StateContext<IGameState>) {
    this.gameService.getRatings().then((res: IRating[]) => {
      if (res) {
        this.store.dispatch(new Game.LoadRatingsSuccess(res))
      } else {
        this.store.dispatch(new Game.LoadRatingsError());
      }
    }).catch(() => {
      this.store.dispatch(new Game.LoadRatingsError());
    });
  }

  @Action(Game.LoadRatingsSuccess)
  loadRatingSuccess(ctx: StateContext<IGameState>, { ratings }: Game.LoadRatingsSuccess) {
    ctx.setState({ ...ctx.getState(), ratings });
  }

  @Action(Game.LoadRatingsError)
  loadRatingError(ctx: StateContext<IGameState>) {
    ctx.setState({ ...ctx.getState(), error: 'Error by loading ratings.' });
  }



  /**
   * Load Board Games
   */
  @Action(Game.LoadBoardGames)
  loadBoardGames(ctx: StateContext<IGameState>) {
    this.gameService.getBoardGames().then(res => {
      if (Array.isArray(res)) {
        this.store.dispatch(new Game.LoadBoardGamesSuccess(res))
      } else {
        this.store.dispatch(new Game.LoadBoardGamesError());
      }
    }).catch(() => {
      this.store.dispatch(new Game.LoadBoardGamesError());
    });
  }

  @Action(Game.LoadBoardGamesSuccess)
  loadBoardGamesSuccess(ctx: StateContext<IGameState>, { boardGames }: Game.LoadBoardGamesSuccess) {
    ctx.setState({ ...ctx.getState(), boardGames });
  }

  @Action(Game.LoadBoardGamesError)
  loadBoardGamesError(ctx: StateContext<IGameState>) {
    ctx.setState({ ...ctx.getState(), error: 'Error by loading games.' });
  }


  /**
   * Load Board Game Recommendations
   */
  @Action(Game.LoadRecommendedBoardGames)
  loadRecommendedBoardGames(ctx: StateContext<IGameState>) {
    this.gameService.getRecommendedBoardGames().then(res => {
      if (Array.isArray(res)) {
        this.store.dispatch(new Game.LoadRecommendedBoardGamesSuccess(res))
      } else {
        this.store.dispatch(new Game.LoadRecommendedBoardGamesError());
      }
    }).catch(() => {
      this.store.dispatch(new Game.LoadRecommendedBoardGamesError());
    });
  }

  @Action(Game.LoadRecommendedBoardGamesSuccess)
  loadRecommendedBoardGamesSuccess(ctx: StateContext<IGameState>, { recommendedBoardGames }: Game.LoadRecommendedBoardGamesSuccess) {
    ctx.setState({ ...ctx.getState(), recommendedBoardGames });
  }

  @Action(Game.LoadRecommendedBoardGamesError)
  loadRecommendedBoardGamesError(ctx: StateContext<IGameState>) {
    ctx.setState({ ...ctx.getState(), error: 'Error by loading recommended games.' });
  }


}