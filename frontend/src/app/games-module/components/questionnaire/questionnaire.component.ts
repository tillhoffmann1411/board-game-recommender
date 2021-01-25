import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { IBoardGame, IRating } from 'src/app/models/game';
import { GameStore } from 'src/app/storemanagement/game.store';


@Component({
  selector: 'app-questionnaire',
  templateUrl: './questionnaire.component.html',
  styleUrls: ['./questionnaire.component.scss']
})
export class QuestionnaireComponent implements OnInit {
  searchControl = new FormControl();
  games: IBoardGame[];
  filteredGames: Observable<IBoardGame[]>;
  ratings: IRating[] = [];
  isLoading = true;


  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private gameService: GameStore,
  ) { }

  ngOnInit(): void {
    this.gameService.getRatings.subscribe(ratings => this.ratings = ratings);
    this.gameService.getBoardGames.subscribe(games => {
      if (games.length > 0) {
        this.isLoading = false;
      }
      this.games = games;

      this.filteredGames = this.searchControl.valueChanges.pipe(
        startWith(''),
        map(searchInput => this._filter(searchInput)),
        map(boardGames => boardGames.slice(0, 15))
      );
    });
  }

  getRatingForGame(gameId: number): undefined | number {
    return this.ratings.find(r => r.game === gameId)?.rating;
  }

  next() {
    this.router.navigate(['recommendations'], { relativeTo: this.route });
  }

  /**
   * Function is from angular material Docu 
   * https://material.angular.io/components/autocomplete/examples
   */
  private _filter(searchInput: string): IBoardGame[] {
    const filterValue = this._normalizeValue(searchInput);
    return this.games.filter(game => this._normalizeValue(game.name).includes(filterValue));
  }
  /**
   * Function is from angular material Docu 
   * https://material.angular.io/components/autocomplete/examples
   */
  private _normalizeValue(value: string): string {
    return value.toLowerCase().replace(/\s/g, '');
  }

}
