import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatCardModule } from '@angular/material/card';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatInputModule } from '@angular/material/input';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatExpansionModule } from '@angular/material/expansion';
import { StarRatingComponent } from './star-rating/star-rating.component';
import { MatPaginatorModule } from '@angular/material/paginator';
import { LoadingComponent } from './loading/loading.component';
import { LottieModule } from 'ngx-lottie';




@NgModule({
  declarations: [
    StarRatingComponent,
    LoadingComponent
  ],
  imports: [
    CommonModule,
    MatSidenavModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatTooltipModule,
    MatInputModule,
    MatAutocompleteModule,
    MatExpansionModule,
    MatPaginatorModule,
    LottieModule,
  ],
  exports: [
    MatSidenavModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatListModule,
    MatCardModule,
    MatTooltipModule,
    MatInputModule,
    MatAutocompleteModule,
    MatExpansionModule,
    StarRatingComponent,
    MatPaginatorModule,
    LoadingComponent,
  ],
})
export class MaterialModule { }