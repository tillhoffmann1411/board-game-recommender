export interface IGameState {
  boardGames: IBoardGame[];
  recommendedBoardGames: {
    commonBased: IRecResponse[],
    knn: IRecResponse[],
    itemBased: IRecResponse[]
  };
  ratings: IRating[];
  isLoading: boolean;
  error: string;
}

export interface IRecResponse {
  gameKey: number,
  estimate?: number,
  0?: number
}

export interface IBoardGame {
  id: number;
  name: string;
  description: string;
  imageUrl?: string;
  yearPublished?: number;
  minPlaytime?: number;
  maxPlaytime?: number;
  minNumberOfPlayers?: number;
  maxNumberOfPlayers?: number;
  minAge?: number;
  bggAvgRating?: number;
  bgaAvgRating?: number;
  bggRating?: number;
  bgaRating?: number;
  officialUrl?: string;
  thumbnailUrl?: string;
  bgaUrl?: string;
  author?: IAuthor[];
  categories?: ICategories[];
  gameMechanic?: IGameMechanic[];
  publisher?: IPublisher[];
}


export interface IOnlineGame {
  id: number;
  name: string;
  description: string;
  imageUrl?: string;
  yearPublished?: number;
  minPlaytime?: number;
  maxPlaytime?: number;
  minNumberOfPlayers?: number;
  maxNumberOfPlayers?: number;
  minAge?: number;
  author?: IAuthor[];
  categories?: ICategories[];
  gameMechanic?: IGameMechanic[];
  publisher?: IPublisher[];
}

export interface IRating {
  id?: number,
  game: number,
  rating: number,
  createdAt?: Date,
  createdBy?: number,
}


export interface IAuthor {
  id: string;
  name: string;
  url?: string;
  imageUrl?: string;
}

export interface IPublisher {
  id: string;
  name: string;
  url?: string;
  imageUrl?: string;
}

export interface ICategories {
  id: number;
  name: string;
  bgaUrl?: string;
}

export interface IGameMechanic {
  id: number;
  name: string;
  bgaUrl?: string;
}
