export type TossSelection = "" | "HOME_FIELD" | "HOME_BAT" | "AWAY_FIELD" | "AWAY_BAT";

export type BulletNumber = 0 | 1 | 2 | 3;

export interface BulletInput {
    odds: string;
    stake: string;
}

export type BulletInputState = Record<BulletNumber, BulletInput>;

export type HomeGround = "FAV" | "UG" | "NEU";

export interface OddsPhaseInput {
    selectedTeam: string;
    backOdds: string;
    layOdds: string;
}
