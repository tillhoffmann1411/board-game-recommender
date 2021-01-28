import { Component, OnInit } from '@angular/core';
import { IBoardGame, IGameState, IRecResponse } from 'src/app/models/game';
import { GameStore } from 'src/app/storemanagement/game.store';

@Component({
  selector: 'app-recommendation',
  templateUrl: './recommendation.component.html',
  styleUrls: ['./recommendation.component.scss']
})
export class RecommendationComponent implements OnInit {
  recommendations: IGameState['recommendedBoardGames'];
  commonBased: IBoardGame[] = [];
  knn: IBoardGame[] = [];
  itemBased: IBoardGame[] = [];

  gameMap: Map<number, IBoardGame> = new Map();

  isLoading = false;
  largeScreen = document.body.clientWidth > 768;

  minAge = -1;
  player: { min: number, max: number } = { min: -1, max: -1 };
  time: { min: number, max: number } = { min: -1, max: -1 };


  constructor(
    private gameService: GameStore,
  ) { }

  ngOnInit(): void {
    window.addEventListener('resize', (event) => {
      this.largeScreen = document.body.clientWidth > 768;
    });
    this.isLoading = true;
    this.gameService.getBoardGames.subscribe(games => {
      this.gameService.getRecommendedBoardGames.subscribe(recommendations => {
        if (games.length > 0 &&
          (recommendations.commonBased.length > 0 ||
            recommendations.knn.length > 0 ||
            recommendations.itemBased.length > 0)) {
          this.isLoading = false;
        }
        games.forEach(g => {
          if ((g.minAge && this.minAge === -1) || (g.minAge && this.minAge < g.minAge)) this.minAge = g.minAge
          if ((g.minNumberOfPlayers && this.player.min === -1) || g.minNumberOfPlayers && this.player.min > g.minNumberOfPlayers) this.player.min = g.minNumberOfPlayers
          if ((g.maxNumberOfPlayers && this.player.max === -1) || g.maxNumberOfPlayers && this.player.max < g.maxNumberOfPlayers) this.player.max = g.maxNumberOfPlayers
          if ((g.minPlaytime && this.time.min === -1) || g.minPlaytime && this.time.min > g.minPlaytime) this.time.min = g.minPlaytime
          if ((g.maxPlaytime && this.time.max === -1) || g.maxPlaytime && this.time.max < g.maxPlaytime) this.time.max = g.maxPlaytime

          this.gameMap.set(g.id, g)
        });
        this.recommendations = recommendations;
        this.commonBased = this.getGameListFromKeys(recommendations.commonBased, this.gameMap);
        this.knn = this.getGameListFromKeys(recommendations.knn, this.gameMap);
        this.itemBased = this.getGameListFromKeys(recommendations.itemBased, this.gameMap);
      });
    });
  }

  getGameListFromKeys(recommendations: IRecResponse[], games: Map<number, IBoardGame>) {
    const newList: IBoardGame[] = [];
    if (recommendations.length > 0) {
      for (let i = 0; i < 50; i++) {
        if (recommendations[i]) {
          const game = games.get(recommendations[i].gameKey);
          if (game) {
            newList.push(game);
          }
          continue;
        } else {
          break;
        }
      }
    }
    return newList;
  }

  minusMinAge() {
    this.minAge = this.minAge < 0 ? -1 : this.minAge - 1;
  }

  plusMinAge() {
    this.minAge = this.minAge > 99 ? 100 : this.minAge + 1;
  }

  filter() {
    console.log(this.minAge, this.player, this.time);
    const filteredGames: Map<number, IBoardGame> = new Map();
    this.gameMap.forEach((game, id) => {
      if (
        game.minAge && game.minAge <= this.minAge &&
        game.minNumberOfPlayers && game.minNumberOfPlayers >= this.player.min &&
        game.maxNumberOfPlayers && game.maxNumberOfPlayers <= this.player.max &&
        game.minPlaytime && game.minPlaytime >= this.time.min &&
        game.maxPlaytime && game.maxPlaytime <= this.time.max
      ) {
        filteredGames.set(id, game);
      }
    });
    this.commonBased = this.getGameListFromKeys(this.recommendations.commonBased, filteredGames);
    this.knn = this.getGameListFromKeys(this.recommendations.knn, filteredGames);
    this.itemBased = this.getGameListFromKeys(this.recommendations.itemBased, filteredGames);
  }

}