import { Store, Select } from '@ngxs/store';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { IBoardGame, IGameState, IRating, IRecommenderState } from '../models/game';
import { GameState } from './state/game.state';
import { Game } from './state/game.actions';
import { RecommenderState } from './state/recommender.state';
import { Recommender } from './state/recommender.actions';

@Injectable({
  providedIn: 'root'
})
export class GameStore {

  constructor(private store: Store) { }

  @Select(GameState.getBoardGames)
  public getBoardGames: Observable<IBoardGame[]>;

  @Select(RecommenderState.getRecommendedBoardGames)
  public getRecommendedBoardGames: Observable<IRecommenderState>;

  @Select(GameState.getRatings)
  public getRatings: Observable<IRating[]>;

  @Select(GameState.isLoading)
  public isLoading: Observable<boolean>;


  getBoardGamesSnapshot(): IBoardGame[] {
    return this.store.selectSnapshot<IGameState>(state => state).boardGames;
  }

  getRecommendedBoardGamesSnapshot(): IRecommenderState {
    return this.store.selectSnapshot<IRecommenderState>(state => state);
  }

  loadRatings() {
    this.store.dispatch(new Game.LoadRatings());
  }

  loadBoardGames() {
    this.store.dispatch(new Game.LoadBoardGames());
  }

  loadBoardGame(id: number, bggId?: number) {
    this.store.dispatch(new Game.LoadBoardGame(id, bggId));
  }

  loadRecommendedCommonBased() {
    this.store.dispatch(new Recommender.LoadRecommendationCommonBased());
  }

  loadRecommendedKNN() {
    this.store.dispatch(new Recommender.LoadRecommendationKNN());
  }

  loadRecommendedItemBased() {
    this.store.dispatch(new Recommender.LoadRecommendationItemBased());
  }

  loadRecommendedPopularity() {
    this.store.dispatch(new Recommender.LoadRecommendationPopularity());
  }

  sendRating(rating: IRating) {
    this.store.dispatch(new Game.SendRating(rating));
  }
}