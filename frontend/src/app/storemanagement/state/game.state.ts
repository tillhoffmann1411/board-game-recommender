import { Injectable } from '@angular/core';
import { Action, Selector, State, StateContext, Store } from '@ngxs/store';
import { IBoardGame, IGameState, IRating } from 'src/app/models/game';
import { GameHttpService } from 'src/app/services/game.service';
import { Game } from './game.actions';

const DEFAULTS: IGameState = {
  boardGames: [],
  recommendedBoardGames: {
    commonBased: [],
    knn: [],
    itemBased: []
  },
  ratings: [],
  isLoading: false,
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

  @Selector()
  static isLoading(state: IGameState) {
    return state.isLoading;
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
    ctx.patchState({ isLoading: true });
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
    this.store.dispatch(new Game.LoadRecommendedBoardGames())
    // this.store.dispatch(new Game.LoadRecommendationKNN())
    // this.store.dispatch(new Game.LoadRecommendationItemBased())

    let joinedGames: IBoardGame[] = []
    if (ctx.getState().boardGames.length > 0) {
      const bgMap: Map<number, IBoardGame> = new Map();
      ctx.getState().boardGames.forEach(g => bgMap.set(g.id, g));
      boardGames.forEach(g => joinedGames.push(bgMap.has(g.id) ? bgMap.get(g.id)! : g));
    } else {
      joinedGames = boardGames;
    }

    ctx.setState({ ...ctx.getState(), boardGames: joinedGames, isLoading: false });
  }

  @Action(Game.LoadBoardGamesError)
  loadBoardGamesError(ctx: StateContext<IGameState>) {
    ctx.setState({ ...ctx.getState(), error: 'Error by loading games.', isLoading: false });
  }


  /**
   * Load single Board Game
   */
  @Action(Game.LoadBoardGame)
  loadBoardGame(ctx: StateContext<IGameState>, { boardGameId }: Game.LoadBoardGame) {
    this.gameService.getBoardGame(boardGameId).then(res => {
      if (res.id) {
        this.store.dispatch(new Game.LoadBoardGameSuccess(res))
      } else {
        this.store.dispatch(new Game.LoadBoardGameError());
      }
    }).catch(() => {
      this.store.dispatch(new Game.LoadBoardGameError());
    });
  }

  @Action(Game.LoadBoardGameSuccess)
  loadBoardGameSuccess(ctx: StateContext<IGameState>, { boardGame }: Game.LoadBoardGameSuccess) {
    let boardGames: IBoardGame[] = []
    if (ctx.getState().boardGames.findIndex(g => g.id == boardGame.id) === -1) {
      boardGames = ctx.getState().boardGames.length > 0 ? ctx.getState().boardGames : [];
      boardGames.push(boardGame);
    } else {
      ctx.getState().boardGames.forEach(game => {
        boardGames.push(game.id === boardGame.id ? boardGame : game);
      });
    }
    ctx.setState({ ...ctx.getState(), boardGames });
  }

  @Action(Game.LoadBoardGameError)
  loadBoardGameError(ctx: StateContext<IGameState>) {
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
  loadRecommendedBoardGamesSuccess(ctx: StateContext<IGameState>, { recommendedBoardGameIds }: Game.LoadRecommendedBoardGamesSuccess) {
    ctx.patchState({ recommendedBoardGames: { ...ctx.getState().recommendedBoardGames, commonBased: recommendedBoardGameIds } });
  }

  @Action(Game.LoadRecommendedBoardGamesError)
  loadRecommendedBoardGamesError(ctx: StateContext<IGameState>) {
    ctx.setState({ ...ctx.getState(), error: 'Error by loading recommended games.' });
  }


  /**
   * Load Board Game Recommendations
   */
  @Action(Game.LoadRecommendationKNN)
  loadRecommendationKNN(ctx: StateContext<IGameState>) {
    this.gameService.getRecommendedKNN().then(res => {
      if (Array.isArray(res)) {
        this.store.dispatch(new Game.LoadRecommendationKNNSuccess(res))
      } else {
        this.store.dispatch(new Game.LoadRecommendationKNNError());
      }
    }).catch(() => {
      this.store.dispatch(new Game.LoadRecommendationKNNError());
    });
  }

  @Action(Game.LoadRecommendationKNNSuccess)
  loadRecommendationKNNSuccess(ctx: StateContext<IGameState>, { knnIds }: Game.LoadRecommendationKNNSuccess) {
    ctx.patchState({ recommendedBoardGames: { ...ctx.getState().recommendedBoardGames, knn: knnIds } });
  }

  @Action(Game.LoadRecommendationKNNError)
  loadRecommendationKNNError(ctx: StateContext<IGameState>) {
    ctx.setState({ ...ctx.getState(), error: 'Error by loading knn recommended games.' });
  }



  /**
   * Load Board Game Recommendations
   */
  @Action(Game.LoadRecommendationItemBased)
  loadRecommendationItemBased(ctx: StateContext<IGameState>) {
    this.gameService.getRecommendedItemBased().then(res => {
      if (Array.isArray(res)) {
        this.store.dispatch(new Game.LoadRecommendationItemBasedSuccess(res))
      } else {
        this.store.dispatch(new Game.LoadRecommendationItemBasedError());
      }
    }).catch(() => {
      this.store.dispatch(new Game.LoadRecommendationItemBasedError());
    });
  }

  @Action(Game.LoadRecommendationItemBasedSuccess)
  loadRecommendationItemBasedSuccess(ctx: StateContext<IGameState>, { recIds }: Game.LoadRecommendationItemBasedSuccess) {
    ctx.patchState({ recommendedBoardGames: { ...ctx.getState().recommendedBoardGames, itemBased: recIds } });
  }

  @Action(Game.LoadRecommendationItemBasedError)
  loadRecommendationItemBasedError(ctx: StateContext<IGameState>) {
    ctx.setState({ ...ctx.getState(), error: 'Error by loading item based recommended games.' });
  }

}