import { Component, OnInit } from '@angular/core';
import { IBoardGame, IGameState, IRecommenderState, IRecResponse } from 'src/app/models/game';
import { GameStore } from 'src/app/storemanagement/game.store';

@Component({
  selector: 'app-recommendation',
  templateUrl: './recommendation.component.html',
  styleUrls: ['./recommendation.component.scss']
})
export class RecommendationComponent implements OnInit {
  recommendations: IRecommenderState;
  commonBased: IBoardGame[] = [];
  knn: IBoardGame[] = [];
  itemBased: IBoardGame[] = [];
  popularity: IBoardGame[] = [];

  gameMap: Map<number, IBoardGame> = new Map();

  isLoading = false;
  isLoadingRecommendations = false;
  largeScreen = document.body.clientWidth >= 992;

  minAge = 0;
  player: { min: number, max: number } = { min: 0, max: 0 };
  time: { min: number, max: number } = { min: 0, max: 0 };


  constructor(
    private gameStore: GameStore,
  ) { }

  ngOnInit(): void {
    window.addEventListener('resize', (event) => {
      this.largeScreen = document.body.clientWidth >= 992;
    });
    this.gameStore.isLoading.subscribe(isLoading => this.isLoading = isLoading);
    this.gameStore.isLoadingRecommendations.subscribe(isLoading => this.isLoadingRecommendations = isLoading);

    this.gameStore.getBoardGames.subscribe(games => {
      this.gameStore.getRecommendedBoardGames.subscribe(recommendations => {

        if (games.length > 0 &&
          (recommendations.commonBased.length > 0 ||
            recommendations.knn.length > 0 ||
            recommendations.itemBased.length > 0)) {
        }

        games.forEach(g => this.gameMap.set(g.id, g));

        this.recommendations = recommendations;
        this.commonBased = this.getGameListFromKeys(recommendations.commonBased, this.gameMap);
        this.knn = this.getGameListFromKeys(recommendations.knn, this.gameMap);
        this.itemBased = this.getGameListFromKeys(recommendations.itemBased, this.gameMap);
        this.popularity = this.getGameListFromKeys(recommendations.popularity, this.gameMap);
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

  refresh() {
    this.gameStore.loadRecommendedPopularity();
    this.gameStore.loadRecommendedKNN();
    this.gameStore.loadRecommendedItemBased();
    this.gameStore.loadRecommendedCommonBased();
  }

  filter() {
    const filteredGames: Map<number, IBoardGame> = new Map();
    this.gameMap.forEach((game, id) => {
      if (
        game.minAge && game.minAge >= this.minAge &&
        game.minNumberOfPlayers && game.minNumberOfPlayers >= this.player.min &&
        (this.player.max === 0 || (game.maxNumberOfPlayers && game.maxNumberOfPlayers <= this.player.max)) &&
        game.minPlaytime && game.minPlaytime >= this.time.min &&
        (this.time.max === 0 || (game.maxPlaytime && game.maxPlaytime <= this.time.max))
      ) {
        filteredGames.set(id, game);
      }
    });
    this.commonBased = this.getGameListFromKeys(this.recommendations.commonBased, filteredGames);
    this.knn = this.getGameListFromKeys(this.recommendations.knn, filteredGames);
    this.itemBased = this.getGameListFromKeys(this.recommendations.itemBased, filteredGames);
    this.popularity = this.getGameListFromKeys(this.recommendations.popularity, filteredGames);
  }

}