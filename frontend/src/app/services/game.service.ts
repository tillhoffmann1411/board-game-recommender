import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { IBoardGame, IRecResponse, IRating, ICategory, IMechanic, IAuthor, IPublisher, IOnlineGame } from '../models/game';

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

  getRecommendedCommonBased(): Promise<IRecResponse[]> {
    return this.http.get<IRecResponse[]>(this.baseUrl + '/games/recommendation/common-based/').toPromise();
  }

  getRecommendedKNN(): Promise<IRecResponse[]> {
    return this.http.get<IRecResponse[]>(this.baseUrl + '/games/recommendation/knn/').toPromise();
  }

  getRecommendedItemBased(): Promise<IRecResponse[]> {
    return this.http.get<IRecResponse[]>(this.baseUrl + '/games/recommendation/item-based/').toPromise();
  }

  getRecommendedPopularity(): Promise<IRecResponse[]> {
    return this.http.get<IRecResponse[]>(this.baseUrl + '/games/recommendation/popularity/').toPromise();
  }

  sendRatings(rating: IRating): Promise<IRating> {
    return this.http.post<IRating>(this.baseUrl + '/user/review/', rating).toPromise();
  }

  getRatings(): Promise<IRating[]> {
    return this.http.get<IRating[]>(this.baseUrl + '/user/review/').toPromise();
  }


  getCategories(): Promise<ICategory[]> {
    return this.http.get<ICategory[]>(this.baseUrl + '/games/category/').toPromise();
  }

  getMechanics(): Promise<IMechanic[]> {
    return this.http.get<IMechanic[]>(this.baseUrl + '/games/mechanic/').toPromise();
  }

  getAuthors(): Promise<IAuthor[]> {
    return this.http.get<IAuthor[]>(this.baseUrl + '/games/author/').toPromise();
  }

  getPublishers(): Promise<IPublisher[]> {
    return this.http.get<IPublisher[]>(this.baseUrl + '/games/publisher/').toPromise();
  }

  getOnlineGame(bggid: number): Promise<IOnlineGame> {
    return this.http.get<IOnlineGame>(this.baseUrl + '/games/online-game/' + bggid + '/').toPromise();
  }

}