import { Store, Select } from '@ngxs/store';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { IUser } from '../models/user';
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
  public getRecommendedBoardGames: Observable<IBoardGame[]>;

  @Select(GameState.getRatings)
  public getRatings: Observable<IRating[]>;


  getBoardGamesSnapshot(): IBoardGame[] {
    return this.store.selectSnapshot<IGameState>(state => state).boardGames;
  }

  getRecommendedBoardGamesSnapshot(): IBoardGame[] {
    return this.store.selectSnapshot<IGameState>(state => state).recommendedBoardGames;
  }

  loadRatings() {
    this.store.dispatch(new Game.LoadRatings());
  }

  loadBoardGames() {
    this.store.dispatch(new Game.LoadBoardGames());
  }

  loadRecommendedBoardGames() {
    this.store.dispatch(new Game.LoadRecommendedBoardGames());
  }

  sendRating(rating: IRating) {
    this.store.dispatch(new Game.SendRating(rating));
  }
}