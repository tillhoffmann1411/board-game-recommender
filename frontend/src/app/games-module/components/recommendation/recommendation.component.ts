import { Component, OnInit } from '@angular/core';
import { IBoardGame, GAMES } from 'src/app/models/game';

@Component({
  selector: 'app-recommendation',
  templateUrl: './recommendation.component.html',
  styleUrls: ['./recommendation.component.scss']
})
export class RecommendationComponent implements OnInit {
  games: IBoardGame[] = GAMES;

  constructor() { }

  ngOnInit(): void {
  }

}
