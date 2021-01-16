import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { GAMES, IBoardGame, IRating } from '../models/game';

@Injectable({
  providedIn: 'root'
})
export class GameHttpService {

  baseUrl = environment.api.url;
  headers: HttpHeaders = new HttpHeaders().append('Accept', 'application/json');

  constructor(private http: HttpClient) { }

  getBoardGames(): Promise<IBoardGame[]> {
    return Promise.resolve(GAMES);
    // return this.http.get<IBoardGame[]>(this.baseUrl + '/games/').toPromise();
  }

  getRecommendedBoardGames(): Promise<IBoardGame[]> {
    return Promise.resolve(GAMES);
  }

  sendRatings(rating: IRating): Promise<string> {
    return Promise.resolve('Uploaded ratings');
    // return this.http.post<string>(this.baseUrl + '/games/ratings/', { ratings }).toPromise();
  }
}