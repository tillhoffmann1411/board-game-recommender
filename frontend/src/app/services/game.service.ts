import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { IBoardGame, IRecResponse, IRating } from '../models/game';

@Injectable({
  providedIn: 'root'
})
export class GameHttpService {

  baseUrl = environment.api.url;
  headers: HttpHeaders = new HttpHeaders().append('Accept', 'application/json');

  constructor(private http: HttpClient) { }

  getBoardGames(): Promise<IBoardGame[]> {
    return this.http.get<IBoardGame[]>(this.baseUrl + '/games/').toPromise();
  }

  getBoardGame(id: number): Promise<IBoardGame> {
    return this.http.get<IBoardGame>(this.baseUrl + '/games/' + id + '/').toPromise();
  }

  getRecommendedBoardGames(): Promise<IRecResponse[]> {
    return this.http.get<IRecResponse[]>(this.baseUrl + '/games/recommendation/').toPromise();
  }

  getRecommendedKNN(): Promise<IRecResponse[]> {
    return this.http.get<IRecResponse[]>(this.baseUrl + '/games/recommendation/knn/').toPromise();
  }

  getRecommendedItemBased(): Promise<IRecResponse[]> {
    return this.http.get<IRecResponse[]>(this.baseUrl + '/games/recommendation/item-based/').toPromise();
  }

  sendRatings(rating: IRating): Promise<IRating> {
    return this.http.post<IRating>(this.baseUrl + '/user/review/', rating).toPromise();
  }

  getRatings(): Promise<IRating[]> {
    return this.http.get<IRating[]>(this.baseUrl + '/user/review/').toPromise();
  }
}