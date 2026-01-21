import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { DetailComponent } from './components/detail/detail.component';

import { QuestionnaireComponent } from './components/questionnaire/questionnaire.component';
import { RecommendationComponent } from './components/recommendation/recommendation.component';
import { UserRatingsComponent } from './components/user-ratings/user-ratings.component';

const routes: Routes = [
  { path: 'recommendations', component: RecommendationComponent },
  { path: 'detail', component: DetailComponent },
  { path: 'user-ratings', component: UserRatingsComponent },
  { path: '', component: QuestionnaireComponent },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class GamesModuleRoutingModule { }
