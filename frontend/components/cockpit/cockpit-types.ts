export type TossSelection = "" | "HOME_FIELD" | "HOME_BAT" | "AWAY_FIELD" | "AWAY_BAT";

export type BulletNumber = 0 | 1 | 2 | 3;

export interface BulletInput {
    odds: string;
    stake: string;
}

export type BulletInputState = Record<BulletNumber, BulletInput>;

export type HomeGround = "FAV" | "UG" | "NEU";

/* ── Live data types (Santhel scraper) ───────────────────────────────── */

export interface LiveBall {
    value: string;
    type: "dot" | "run" | "four" | "six" | "wicket";
}

export interface LiveTeamScore {
    name: string;
    runs: number;
    wickets: number;
    overs: string;
    crr: number | null;
}

export interface LiveData {
    score: {
        team1: LiveTeamScore;
        team2: LiveTeamScore;
        balls: LiveBall[];
    };
    odds: {
        team1_back: number;
        team2_back: number;
    };
    last_updated: string;
}

export interface SanthelSettings {
    username: string;
    password_set: boolean;
}
