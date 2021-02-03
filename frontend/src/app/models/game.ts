export interface IGameState {
  boardGames: IBoardGame[];
  ratings: IRating[];
  advancedInfos: {
    categories: ICategory[];
    mechanics: IMechanic[];
    authors: IAuthor[];
    publishers: IPublisher[];
  };
  isLoading: boolean;
  error: string;
}

export interface IRecommenderState {
  commonBased: IRecResponse[],
  knn: IRecResponse[],
  itemBased: IRecResponse[],
  popularity: IRecResponse[],
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
  bggId?: number;
  bggAvgRating?: number;
  bgaAvgRating?: number;
  bggRating?: number;
  bgaId?: string;
  bgaRating?: number;
  officialUrl?: string;
  thumbnailUrl?: string;
  bgaUrl?: string;
  author?: IAuthor[];
  category?: ICategory[];
  gameMechanic?: IMechanic[];
  publisher?: IPublisher[];
  onlineGames?: IOnlineGame[];
}


export interface IOnlineGame {
  id: number;
  name: string;
  origin: string;
  url: string;
  bggId: string
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

export interface ICategory {
  id: number;
  name: string;
  bgaUrl?: string;
}

export interface IMechanic {
  id: number;
  name: string;
  bgaUrl?: string;
}
