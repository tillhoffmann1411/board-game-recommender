import { Store, Select } from '@ngxs/store';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { IBoardGame, IGameState, IRating } from '../models/game';
import { GameState } from './state/game.state';
import { Game } from './state/game.actions';

@Injectable({
  providedIn: 'root'
})
export class GameStore {

  constructor(private store: Store) { }

  @Select(GameState.getBoardGames)
  public getBoardGames: Observable<IBoardGame[]>;

  @Select(GameState.getRecommendedBoardGames)
  public getRecommendedBoardGames: Observable<IGameState['recommendedBoardGames']>;

  @Select(GameState.getRatings)
  public getRatings: Observable<IRating[]>;

  @Select(GameState.isLoading)
  public isLoading: Observable<boolean>;


  getBoardGamesSnapshot(): IBoardGame[] {
    return this.store.selectSnapshot<IGameState>(state => state).boardGames;
  }

  getRecommendedBoardGamesSnapshot(): IGameState['recommendedBoardGames'] {
    return this.store.selectSnapshot<IGameState>(state => state).recommendedBoardGames;
  }

  loadRatings() {
    this.store.dispatch(new Game.LoadRatings());
  }

  loadBoardGames() {
    this.store.dispatch(new Game.LoadBoardGames());
  }

  loadBoardGame(id: number) {
    this.store.dispatch(new Game.LoadBoardGame(id));
  }

  loadRecommendedBoardGames() {
    this.store.dispatch(new Game.LoadRecommendedBoardGames());
  }

  loadRecommendedKNN() {
    this.store.dispatch(new Game.LoadRecommendationKNN());
  }

  loadRecommendedItemBased() {
    this.store.dispatch(new Game.LoadRecommendationItemBased());
  }

  sendRating(rating: IRating) {
    this.store.dispatch(new Game.SendRating(rating));
  }
}