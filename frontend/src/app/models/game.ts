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
  author?: IAuthor[];
  categories?: ICategories[];
  gameMechanic?: IGameMechanic[];
  publisher?: IPublisher[];
}


export interface IAuthor {
  id: string;
  name: string;
  bgaUrl?: string;
}

export interface ICategories {
  id: number;
  name: string;
}

export interface IPublisher {
  id: string;
  name: string;
  bgaUrl?: string;
}

export interface IGameMechanic {
  id: number;
  name: string;
}



export const GAMES: IBoardGame[] = [
  { id: 1, name: 'Gloomhaven', description: 'Players take the part of land owners, attempting to buy and then develop their land. ', imageUrl: 'https://cf.geekdo-images.com/sZYp_3BTDGjh2unaZfZmuA__itemrep/img/0IdBRA_G-ZdrNaxI4Z1LPQMZD0I=/fit-in/246x300/filters:strip_icc()/pic2437871.jpg', yearPublished: 1933, minPlaytime: 60, maxPlaytime: 180, minNumberOfPlayers: 2, maxNumberOfPlayers: 8, minAge: 8, author: [{ id: 'fs32', name: 'Elizabeth J. Magie' }], categories: [{ id: 3, name: 'Economic' }, { id: 6, name: 'Negotiation' }], gameMechanic: [{ id: 4, name: 'Austion/Bidding' }, { id: 44, name: 'Income' }], publisher: [{ id: 'fa2', name: 'Alga' }] },
  { id: 2, name: 'Pandemic Legacy: Season 1', description: 'Gloomhaven is a game of Euro-inspired tactical combat in a persistent world of shifting motives. Players will take on the role of a wandering adventurer with their own special set of skills and their own reasons for traveling to this dark corner of the world. Players must work together out of necessity to clear out menacing dungeons and forgotten ruins.', imageUrl: 'https://cf.geekdo-images.com/-Qer2BBPG7qGGDu6KcVDIw__itemrep/img/Wxe36yaTzpiIVhEefHOYzFv7Ucc=/fit-in/246x300/filters:strip_icc()/pic2452831.png', yearPublished: 2017, minPlaytime: 60, maxPlaytime: 120, minNumberOfPlayers: 1, maxNumberOfPlayers: 4, minAge: 14, author: [{ id: 'fs32', name: 'Elizabeth J. Magie' }], categories: [{ id: 3, name: 'Economic' }, { id: 6, name: 'Negotiation' }], gameMechanic: [{ id: 4, name: 'Austion/Bidding' }, { id: 44, name: 'Income' }], publisher: [{ id: 'fa2', name: 'Alga' }] },
  { id: 3, name: 'Brass: Birmingham', description: 'Players take the part of land owners, attempting to buy and then develop their land. ', imageUrl: 'https://cf.geekdo-images.com/x3zxjr-Vw5iU4yDPg70Jgw__itemrep/img/giNUMut4HAl-zWyQkGG0YchmuLI=/fit-in/246x300/filters:strip_icc()/pic3490053.jpg', yearPublished: 2015, minPlaytime: 60, maxPlaytime: 180, minNumberOfPlayers: 2, maxNumberOfPlayers: 4, minAge: 13, author: [{ id: 'fs32', name: 'Elizabeth J. Magie' }], categories: [{ id: 3, name: 'Economic' }, { id: 6, name: 'Negotiation' }], gameMechanic: [{ id: 4, name: 'Austion/Bidding' }, { id: 44, name: 'Income' }], publisher: [{ id: 'fa2', name: 'Alga' }] },
  { id: 4, name: 'Terraforming Mars', description: 'Players take the part of land owners, attempting to buy and then develop their land. ', imageUrl: 'https://cf.geekdo-images.com/wg9oOLcsKvDesSUdZQ4rxw__itemrep/img/IwUOQfhP5c0KcRJBY4X_hi3LpsY=/fit-in/246x300/filters:strip_icc()/pic3536616.jpg', yearPublished: 1933, minPlaytime: 60, maxPlaytime: 180, minNumberOfPlayers: 2, maxNumberOfPlayers: 8, minAge: 8, author: [{ id: 'fs32', name: 'Elizabeth J. Magie' }], categories: [{ id: 3, name: 'Economic' }, { id: 6, name: 'Negotiation' }], gameMechanic: [{ id: 4, name: 'Austion/Bidding' }, { id: 44, name: 'Income' }], publisher: [{ id: 'fa2', name: 'Alga' }] },
  { id: 5, name: 'Twilight Imperium: Fourth Edition', description: 'Players take the part of land owners, attempting to buy and then develop their land. ', imageUrl: 'https://cf.geekdo-images.com/_Ppn5lssO5OaildSE-FgFA__itemrep/img/rJfEVG0xStfVWbevNWfHBo4ZVrQ=/fit-in/246x300/filters:strip_icc()/pic3727516.jpg', yearPublished: 1933, minPlaytime: 60, maxPlaytime: 180, minNumberOfPlayers: 2, maxNumberOfPlayers: 8, minAge: 8, author: [{ id: 'fs32', name: 'Elizabeth J. Magie' }], categories: [{ id: 3, name: 'Economic' }, { id: 6, name: 'Negotiation' }], gameMechanic: [{ id: 4, name: 'Austion/Bidding' }, { id: 44, name: 'Income' }], publisher: [{ id: 'fa2', name: 'Alga' }] },
  { id: 6, name: 'Through the Ages: A New Story of Civilization', description: 'Players take the part of land owners, attempting to buy and then develop their land. ', imageUrl: 'https://cf.geekdo-images.com/fVwPntkJKgaEo0rIC0RwpA__itemrep/img/TF5TpehpgE7XvNSRzSSWjnYCbLc=/fit-in/246x300/filters:strip_icc()/pic2663291.jpg', yearPublished: 1933, minPlaytime: 60, maxPlaytime: 180, minNumberOfPlayers: 2, maxNumberOfPlayers: 8, minAge: 8, author: [{ id: 'fs32', name: 'Elizabeth J. Magie' }], categories: [{ id: 3, name: 'Economic' }, { id: 6, name: 'Negotiation' }], gameMechanic: [{ id: 4, name: 'Austion/Bidding' }, { id: 44, name: 'Income' }], publisher: [{ id: 'fa2', name: 'Alga' }] },
  { id: 7, name: 'Monopoly', description: 'Players take the part of land owners, attempting to buy and then develop their land. ', imageUrl: 'https://cf.geekdo-images.com/9nGoBZ0MRbi6rdH47sj2Qg__itemrep/img/8EP4ErNA709diOt6fUyJH30FtbU=/fit-in/246x300/filters:strip_icc()/pic5786795.jpg', yearPublished: 1933, minPlaytime: 60, maxPlaytime: 180, minNumberOfPlayers: 2, maxNumberOfPlayers: 8, minAge: 8, author: [{ id: 'fs32', name: 'Elizabeth J. Magie' }], categories: [{ id: 3, name: 'Economic' }, { id: 6, name: 'Negotiation' }], gameMechanic: [{ id: 4, name: 'Austion/Bidding' }, { id: 44, name: 'Income' }], publisher: [{ id: 'fa2', name: 'Alga' }] },
  { id: 1, name: 'Gloomhaven', description: 'Players take the part of land owners, attempting to buy and then develop their land. ', imageUrl: 'https://cf.geekdo-images.com/sZYp_3BTDGjh2unaZfZmuA__itemrep/img/0IdBRA_G-ZdrNaxI4Z1LPQMZD0I=/fit-in/246x300/filters:strip_icc()/pic2437871.jpg', yearPublished: 1933, minPlaytime: 60, maxPlaytime: 180, minNumberOfPlayers: 2, maxNumberOfPlayers: 8, minAge: 8, author: [{ id: 'fs32', name: 'Elizabeth J. Magie' }], categories: [{ id: 3, name: 'Economic' }, { id: 6, name: 'Negotiation' }], gameMechanic: [{ id: 4, name: 'Austion/Bidding' }, { id: 44, name: 'Income' }], publisher: [{ id: 'fa2', name: 'Alga' }] },
  { id: 2, name: 'Pandemic Legacy: Season 1', description: 'Gloomhaven is a game of Euro-inspired tactical combat in a persistent world of shifting motives. Players will take on the role of a wandering adventurer with their own special set of skills and their own reasons for traveling to this dark corner of the world. Players must work together out of necessity to clear out menacing dungeons and forgotten ruins.', imageUrl: 'https://cf.geekdo-images.com/-Qer2BBPG7qGGDu6KcVDIw__itemrep/img/Wxe36yaTzpiIVhEefHOYzFv7Ucc=/fit-in/246x300/filters:strip_icc()/pic2452831.png', yearPublished: 2017, minPlaytime: 60, maxPlaytime: 120, minNumberOfPlayers: 1, maxNumberOfPlayers: 4, minAge: 14, author: [{ id: 'fs32', name: 'Elizabeth J. Magie' }], categories: [{ id: 3, name: 'Economic' }, { id: 6, name: 'Negotiation' }], gameMechanic: [{ id: 4, name: 'Austion/Bidding' }, { id: 44, name: 'Income' }], publisher: [{ id: 'fa2', name: 'Alga' }] },
  { id: 3, name: 'Brass: Birmingham', description: 'Players take the part of land owners, attempting to buy and then develop their land. ', imageUrl: 'https://cf.geekdo-images.com/x3zxjr-Vw5iU4yDPg70Jgw__itemrep/img/giNUMut4HAl-zWyQkGG0YchmuLI=/fit-in/246x300/filters:strip_icc()/pic3490053.jpg', yearPublished: 2015, minPlaytime: 60, maxPlaytime: 180, minNumberOfPlayers: 2, maxNumberOfPlayers: 4, minAge: 13, author: [{ id: 'fs32', name: 'Elizabeth J. Magie' }], categories: [{ id: 3, name: 'Economic' }, { id: 6, name: 'Negotiation' }], gameMechanic: [{ id: 4, name: 'Austion/Bidding' }, { id: 44, name: 'Income' }], publisher: [{ id: 'fa2', name: 'Alga' }] },
  { id: 4, name: 'Terraforming Mars', description: 'Players take the part of land owners, attempting to buy and then develop their land. ', imageUrl: 'https://cf.geekdo-images.com/wg9oOLcsKvDesSUdZQ4rxw__itemrep/img/IwUOQfhP5c0KcRJBY4X_hi3LpsY=/fit-in/246x300/filters:strip_icc()/pic3536616.jpg', yearPublished: 1933, minPlaytime: 60, maxPlaytime: 180, minNumberOfPlayers: 2, maxNumberOfPlayers: 8, minAge: 8, author: [{ id: 'fs32', name: 'Elizabeth J. Magie' }], categories: [{ id: 3, name: 'Economic' }, { id: 6, name: 'Negotiation' }], gameMechanic: [{ id: 4, name: 'Austion/Bidding' }, { id: 44, name: 'Income' }], publisher: [{ id: 'fa2', name: 'Alga' }] },
  { id: 5, name: 'Twilight Imperium: Fourth Edition', description: 'Players take the part of land owners, attempting to buy and then develop their land. ', imageUrl: 'https://cf.geekdo-images.com/_Ppn5lssO5OaildSE-FgFA__itemrep/img/rJfEVG0xStfVWbevNWfHBo4ZVrQ=/fit-in/246x300/filters:strip_icc()/pic3727516.jpg', yearPublished: 1933, minPlaytime: 60, maxPlaytime: 180, minNumberOfPlayers: 2, maxNumberOfPlayers: 8, minAge: 8, author: [{ id: 'fs32', name: 'Elizabeth J. Magie' }], categories: [{ id: 3, name: 'Economic' }, { id: 6, name: 'Negotiation' }], gameMechanic: [{ id: 4, name: 'Austion/Bidding' }, { id: 44, name: 'Income' }], publisher: [{ id: 'fa2', name: 'Alga' }] },
  { id: 6, name: 'Through the Ages: A New Story of Civilization', description: 'Players take the part of land owners, attempting to buy and then develop their land. ', imageUrl: 'https://cf.geekdo-images.com/fVwPntkJKgaEo0rIC0RwpA__itemrep/img/TF5TpehpgE7XvNSRzSSWjnYCbLc=/fit-in/246x300/filters:strip_icc()/pic2663291.jpg', yearPublished: 1933, minPlaytime: 60, maxPlaytime: 180, minNumberOfPlayers: 2, maxNumberOfPlayers: 8, minAge: 8, author: [{ id: 'fs32', name: 'Elizabeth J. Magie' }], categories: [{ id: 3, name: 'Economic' }, { id: 6, name: 'Negotiation' }], gameMechanic: [{ id: 4, name: 'Austion/Bidding' }, { id: 44, name: 'Income' }], publisher: [{ id: 'fa2', name: 'Alga' }] },
  { id: 7, name: 'Monopoly', description: 'Players take the part of land owners, attempting to buy and then develop their land. ', imageUrl: 'https://cf.geekdo-images.com/9nGoBZ0MRbi6rdH47sj2Qg__itemrep/img/8EP4ErNA709diOt6fUyJH30FtbU=/fit-in/246x300/filters:strip_icc()/pic5786795.jpg', yearPublished: 1933, minPlaytime: 60, maxPlaytime: 180, minNumberOfPlayers: 2, maxNumberOfPlayers: 8, minAge: 8, author: [{ id: 'fs32', name: 'Elizabeth J. Magie' }], categories: [{ id: 3, name: 'Economic' }, { id: 6, name: 'Negotiation' }], gameMechanic: [{ id: 4, name: 'Austion/Bidding' }, { id: 44, name: 'Income' }], publisher: [{ id: 'fa2', name: 'Alga' }] },
]