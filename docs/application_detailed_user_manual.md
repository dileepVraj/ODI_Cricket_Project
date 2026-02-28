# Application Detailed User Manual

Last updated: 2026-02-19
Scope: ODI format (manifest-driven UI/API flow)

## 1. Purpose
This manual documents end-user behavior for key application functions, with formal contract details for `Host Country H2H` in `Rivalry Lab`.

## 2. Host Country H2H

Function key: `country_h2h`  
Engine method: `TeamEngine.analyze_country_h2h`  
Output type: `comparison_table`

This function analyzes Team A vs Team B performance restricted to matches hosted in a selected country.

## 3. Input Contract

Required:
- `team_a` (Home Team)
- `years`

Optional:
- `team_b` (Away Team)
- `country_name` (Host Country)

UI support:
- `country_name` is driven by dropdown source: `/api/v1/{format}/context/host_countries`
- Dropdown empty option text: `Home Team Country (Default)`

## 4. Behavior Matrix

1. `team_a = X`, `team_b = Y`, `country_name = C`
- Result: `X vs Y` in host country `C`.

2. `team_a = X`, `team_b = Y`, `country_name` empty
- Result: defaults to `X vs Y` in `X` home country (legacy-compatible behavior).

3. `team_a = X`, `team_b = All`, `country_name = C`
- Result: `X vs all opponents` in host country `C`.

4. `team_a = X`, `team_b = All`, `country_name` empty
- Result: defaults to `X vs all opponents` in `X` home country.

## 5. Country Resolution Rules

Primary country filter:
- Uses canonical `venue_id` country prefixes (example: `IND_*` for India).

Fallback country filter (permanent reliability fix):
- If `venue_id` is null or missing for a row, the system resolves country from raw `venue` text via venue alias mapping (`VENUE_MAP`) and then applies prefix logic.
- This prevents valid matches from being dropped due to DAL nulls on `venue_id`.

Why this matters:
- Example match `1384416` has India venue text (`M Chinnaswamy Stadium, Bengaluru`) but null `venue_id`. It is now correctly included for `country_name = India`.

## 6. Match Selection Rules

1. Team pairing
- Specific opponent mode: includes both batting-order permutations (`A vs B` and `B vs A`).
- `All` mode: includes all matches where Team A appears in either innings role.

2. Time window
- Uses lookback from engine reference date (`latest available match date`), not wall-clock now.

3. Smart filter stage
- Applies `apply_smart_filters` before final metric aggregation.

## 7. Output Contract

`country_h2h` always returns:
- `List[Dict[str, Any]]` for successful data
- `[]` when no qualifying matches exist

It must never return `{}` for this renderer type.  
`MATCH_IDS` row is included for audit enrichment.

## 8. API and Manifest Notes

Manifest:
- `required_context`: `["team_a", "years"]`
- `optional_context`: `["team_b"]`
- `extra_inputs.country_name`: dropdown, optional

Context endpoint:
- `GET /api/v1/{format}/context/host_countries`

Execution endpoint:
- `POST /api/v1/{format}/execute/country_h2h`

## 9. Troubleshooting

If UI shows:
- `Rendering as fallback for output type "comparison_table"`

Check:
1. Engine return shape must be `list` or `[]` (not `{}`).
2. Country mapping must include both `venue_id` and raw `venue` resolution paths.
3. Selected country actually has qualifying matches for selected teams and years.

## 10. Change Log (Host Country H2H)

2026-02-19:
1. Made `country_name` optional with default-to-home-country behavior.
2. Enabled `team_b = All` support for host-country analysis.
3. Added host-country dropdown API integration.
4. Fixed null `venue_id` exclusion by resolving country from raw `venue` aliases.
5. Standardized empty output to `[]` for `comparison_table` compatibility.
