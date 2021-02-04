import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { IBoardGame, IRecResponse, IRating, ICategory, IMechanic, IAuthor, IPublisher, IOnlineGame } from '../models/game';

@Injectable({
  providedIn: 'root'
})
export class RecommendationHttpService {

  baseUrl = environment.api.url;
  headers: HttpHeaders = new HttpHeaders().append('Accept', 'application/json');

  constructor(private http: HttpClient) { }

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
}
