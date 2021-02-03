import { Component, OnInit } from '@angular/core';
import { IBoardGame, IRating } from 'src/app/models/game';
import { AuthStore } from 'src/app/storemanagement/auth.store';
import { GameStore } from 'src/app/storemanagement/game.store';

@Component({
  selector: 'app-user-ratings',
  templateUrl: './user-ratings.component.html',
  styleUrls: ['./user-ratings.component.scss']
})
export class UserRatingsComponent implements OnInit {
  isLoading = false;
  allGames: Map<number, IBoardGame> = new Map();
  ratedGames: IBoardGame[];
  ratings: IRating[] = [];
  user: string = '';

  constructor(
    private gameStore: GameStore,
    private authStore: AuthStore
  ) { }

  ngOnInit(): void {
    this.gameStore.isLoading.subscribe(isLoading => this.isLoading = isLoading);

    this.user = this.authStore.getUserSnapshot().username;

    this.gameStore.getRatings.subscribe(ratings => this.ratings = ratings);
    this.gameStore.getBoardGames.subscribe(games => {
      games.forEach(game => this.allGames.set(game.id, game));
      this.ratedGames = this._getRatedGames();
    });
  }

  getRatingForGame(gameId: number): undefined | number {
    return this.ratings.find(r => r.game === gameId)?.rating;
  }

  private _getRatedGames(): IBoardGame[] {
    const ratedGames: Map<number, IBoardGame> = new Map();
    this.ratings.forEach(rating => {
      if (this.allGames.has(rating.game)) {
        ratedGames.set(rating.game, this.allGames.get(rating.game)!);
      }
    });
    return Array.from(ratedGames.values());
  }
}
