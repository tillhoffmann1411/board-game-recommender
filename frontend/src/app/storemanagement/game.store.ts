import { Store, Select } from '@ngxs/store';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { IUser } from '../models/user';
import { IBoardGame } from '../models/game';

@Injectable({
  providedIn: 'root'
})
export class GameStore {

  constructor(private store: Store) { }

  // @Select(GameState.getBoardGames)
  // public getBoardGames: Observable<IBoardGame[]>;

  // @Select(GameState.getRecommendedBoardGames)
  // public getRecommendedBoardGames: Observable<IBoardGame[]>;

  // @Select(GameState.getOnlineGames)
  // public getOnlineGames: Observable<IBoardGame[]>;
}