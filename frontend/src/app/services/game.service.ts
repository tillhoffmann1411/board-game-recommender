import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { IBoardGame, IRating } from '../models/game';

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

  getRecommendedBoardGames(): Promise<{ 'id': number, 'name': string }[]> {
    return this.http.get<{ 'id': number, 'name': string }[]>(this.baseUrl + '/games/recommendation/').toPromise();
  }

  sendRatings(rating: IRating): Promise<IRating> {
    return this.http.post<IRating>(this.baseUrl + '/user/review/', rating).toPromise();
  }

  getRatings(): Promise<IRating[]> {
    return this.http.get<IRating[]>(this.baseUrl + '/user/review/').toPromise();
  }
}