import { Injectable } from '@angular/core';
import { Action, Selector, State, StateContext, Store } from '@ngxs/store';
import { IBoardGame, IGameState, IRating } from 'src/app/models/game';
import { GameHttpService } from 'src/app/services/game.service';
import { Game } from './game.actions';

const DEFAULTS: IGameState = {
  boardGames: [],
  ratings: [],
  advancedInfos: {
    categories: [],
    mechanics: [],
    authors: [],
    publishers: [],
  },
  isLoading: false,
  isLoadingDetails: false,
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
  static getRatings(state: IGameState) {
    return state.ratings;
  }

  @Selector()
  static isLoading(state: IGameState) {
    return state.isLoading;
  }

  @Selector()
  static isLoadingDetails(state: IGameState) {
    return state.isLoadingDetails;
  }

  @Selector()
  static getAdvancedInfos(state: IGameState) {
    return state.advancedInfos;
  }




  /**
   * send Ratings
   */
  @Action(Game.SendRating)
  sendRating(ctx: StateContext<IGameState>, { rating }: Game.SendRating) {
    this.gameService.sendRatings(rating).then(res => {
      if (res) {
        this.store.dispatch(new Game.SendRatingSuccess(res))
      } else {
        this.store.dispatch(new Game.SendRatingError());
      }
    }).catch(() => {
      this.store.dispatch(new Game.SendRatingError());
    });
  }

  @Action(Game.SendRatingSuccess)
  sendRatingSuccess(ctx: StateContext<IGameState>, { rating }: Game.SendRatingSuccess) {
    const oldRatings = new Map<number, IRating>();

    ctx.getState().ratings.forEach(rating => {
      oldRatings.set(rating.game, rating);
    });
    oldRatings.set(rating.game, rating);

    const newRatings: IRating[] = [];
    oldRatings.forEach((review) => {
      newRatings.push(review);
    });
    ctx.setState({ ...ctx.getState(), ratings: newRatings });
  }

  @Action(Game.SendRatingError)
  sendRatingError(ctx: StateContext<IGameState>) {
    ctx.setState({ ...ctx.getState(), error: 'Error by sending ratings.' });
  }


  /**
   * send Ratings
   */
  @Action(Game.DeleteRating)
  deleteRating(ctx: StateContext<IGameState>, { ratingId }: Game.DeleteRating) {
    this.gameService.deleteRating(ratingId).then(() => {
      this.store.dispatch(new Game.DeleteRatingSuccess(ratingId))
    }).catch(() => {
      this.store.dispatch(new Game.DeleteRatingError());
    });
  }

  @Action(Game.DeleteRatingSuccess)
  deleteRatingSuccess(ctx: StateContext<IGameState>, { ratingId }: Game.DeleteRatingSuccess) {
    console.log('before: ', ctx.getState().ratings)
    const newRatings = ctx.getState().ratings.filter(r => r.id !== ratingId)
    console.log('after: ', newRatings)
    ctx.setState({ ...ctx.getState(), ratings: newRatings });
  }

  @Action(Game.DeleteRatingError)
  deleteRatingError(ctx: StateContext<IGameState>) {
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
    ctx.patchState({ isLoadingDetails: true });
    this.gameService.getBoardGame(boardGameId).then(async res => {
      if (res && res.bggId) {
        try {
          const games = await this.gameService.getOnlineGame(res.bggId);
          this.store.dispatch(new Game.LoadBoardGameSuccess({ ...res, onlineGames: [games] }));
        } catch (error) {
          this.store.dispatch(new Game.LoadBoardGameSuccess(res));
        }
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
    ctx.patchState({ isLoadingDetails: false });
    ctx.setState({ ...ctx.getState(), boardGames });
  }

  @Action(Game.LoadBoardGameError)
  loadBoardGameError(ctx: StateContext<IGameState>) {
    ctx.patchState({ isLoadingDetails: false });
    ctx.setState({ ...ctx.getState(), error: 'Error by loading games.' });
  }



  /**
   * Load Categories
   */
  @Action(Game.LoadCategories)
  loadCategories(ctx: StateContext<IGameState>) {
    this.loadGeneric(this.gameService.getCategories(), 'categories');
  }
  @Action(Game.LoadAuthors)
  loadAuthors(ctx: StateContext<IGameState>) {
    this.loadGeneric(this.gameService.getAuthors(), 'authors');
  }
  @Action(Game.LoadMechanics)
  loadMechanics(ctx: StateContext<IGameState>) {
    this.loadGeneric(this.gameService.getMechanics(), 'mechanics');
  }
  @Action(Game.LoadPublishers)
  loadPublishers(ctx: StateContext<IGameState>) {
    this.loadGeneric(this.gameService.getPublishers(), 'publishers');
  }

  loadGeneric(httpCallback: Promise<any[]>, kind: 'categories' | 'mechanics' | 'authors' | 'publishers') {
    httpCallback.then(res => {
      if (res) {
        this.store.dispatch(new Game.LoadGenericSuccess(res, kind))
      } else {
        this.store.dispatch(new Game.LoadGenericError(kind));
      }
    }).catch(() => {
      this.store.dispatch(new Game.LoadGenericError(kind));
    });
  }

  @Action(Game.LoadGenericSuccess)
  loadGenericSuccess(ctx: StateContext<IGameState>, { res, kind }: Game.LoadGenericSuccess) {
    ctx.patchState({ [kind]: res });
  }

  @Action(Game.LoadGenericError)
  loadGenericError(ctx: StateContext<IGameState>, { kind }: Game.LoadGenericError) {
    ctx.setState({ ...ctx.getState(), error: 'Error by loading ' + kind });
  }
}