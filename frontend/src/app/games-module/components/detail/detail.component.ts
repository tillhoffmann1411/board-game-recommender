import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { IAuthor, IBoardGame, ICategory, IMechanic, IOnlineGame, IPublisher, IRating } from 'src/app/models/game';
import { GameStore } from 'src/app/storemanagement/game.store';

interface IInfo {
  icon: string;
  text: string;
  description?: string;
  link?: string
}


@Component({
  selector: 'app-detail',
  templateUrl: './detail.component.html',
  styleUrls: ['./detail.component.scss']
})
export class DetailComponent implements OnInit {
  onlineGames: IBoardGame[] = [];
  game: IBoardGame;
  paramId: number;

  gameInfos: IInfo[] = []
  bgaInfos: IInfo[] = [];
  bggInfos: IInfo[] = [];

  rating = 0;
  userRate: IRating | undefined;

  isLoading = true;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private gameStore: GameStore,
  ) { }

  ngOnInit(): void {
    this.gameStore.isLoadingDetails.subscribe(isLoading => this.isLoading = isLoading);

    this.route.queryParams.subscribe(params => {
      if (params.id) {
        this.paramId = params.id
        this.gameStore.loadBoardGame(this.paramId);
      }
    });
    this.gameStore.getBoardGames.subscribe(games => {
      if (this.paramId) {
        this.game = games.find(g => {
          return g.id == this.paramId;
        })!;
      }
      this.createGameInfos();
    });
    this.gameStore.getRatings.subscribe(ratings => {
      this.userRate = ratings.find(rating => rating.game === this.game?.id);
      this.rating = this.userRate ? this.userRate.rating : 0;
      console.log('User rating:', this.userRate);
      console.log('New ratings: ', this.rating)
    });

    this.onlineGames = [...this.onlineGames].splice(0, 2);
  }

  rate(rating: number) {
    this.gameStore.sendRating({ game: this.game.id, rating });
  }

  goToAmazon() {
    window.open('https://www.amazon.com/s?k=' + this.game.name, '_blank');
  }

  clickOnOnlinegame(onlineGame: IOnlineGame) {
    const url = onlineGame.origin === 'Yucata' ? 'https://' + onlineGame.url : onlineGame.url;
    window.open(url, '_blank');
  }

  clickOnInfo(info: IInfo) {
    if (info.link) {
      window.open(info.link, '_blank');
    }
  }

  removeRating() {
    if (this.userRate?.id) {
      this.gameStore.deleteRating(this.userRate.id);
    }
  }

  createGameInfos() {
    if (this.game) {
      this.gameInfos = [];
      this.bgaInfos = [];
      this.bggInfos = [];

      if (this.game.minNumberOfPlayers) {
        this.gameInfos.push({ icon: 'groups', text: this.game.minNumberOfPlayers + ' - ' + this.game.maxNumberOfPlayers, description: 'Number of players' });
      }
      if (this.game.minPlaytime) {
        this.gameInfos.push({ icon: 'access_time', text: this.game.minPlaytime + ' - ' + this.game.maxPlaytime, description: 'Playtime in minutes' });
      }
      if (this.game.minAge) {
        this.gameInfos.push({ icon: 'person', text: this.game.minAge + '+', description: 'Min age' });
      }
      if (this.game.officialUrl && this.game.officialUrl.length > 5) {
        this.gameInfos.push({ icon: 'link', text: 'Website', description: 'Link to official website', link: this.game.officialUrl });
      }

      // BGG Stuff
      if (this.game.bggRating) {
        this.bggInfos.push({ icon: 'stars', text: 'Rating: ' + this.game.bggRating.toPrecision(2) });
      }
      if (this.game.bggAvgRating) {
        this.bggInfos.push({ icon: 'stars', text: 'Average Rating: ' + this.game.bggAvgRating.toPrecision(2) });
      }

      // BGA Stuff
      if (this.game.bgaRating) {
        this.bgaInfos.push({ icon: 'stars', text: 'Rating: ' + this.game.bgaRating.toPrecision(2) });
      }
      if (this.game.bgaAvgRating) {
        this.bgaInfos.push({ icon: 'stars', text: 'Average Rating: ' + this.game.bgaAvgRating.toPrecision(2) });
      }
      if (this.game.bgaUrl) {
        this.bgaInfos.push({ icon: 'link', text: 'Go to Website', description: 'Link to Board Game Atlas', link: this.game.bgaUrl });
      }
    }
  }
}
