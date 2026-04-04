from core.calculators.team.matchup import (
    ComparisonRowsPayload,
    ContinentPerformanceContext,
    ContinentRowsPayload,
    AwayPerformanceContext,
    CountryH2HContext,
    GlobalH2HContext,
    GlobalH2HStructuredPayload,
    GlobalPerformanceContext,
    HomeDominanceContext,
    MatrixRowsPayload,
    TeamFormContext,
    TeamFormRowsPayload,
    VenueMatchupPayload,
    calculate_away_performance_payload,
    calculate_continent_performance_payload,
    calculate_country_h2h_payload,
    calculate_global_h2h_payload,
    calculate_global_h2h_structured_payload,
    calculate_global_performance_payload,
    calculate_home_dominance_payload,
    calculate_team_form_payload,
)


def test_matchup_package_exports() -> None:
    assert calculate_global_h2h_payload is not None
    assert calculate_global_h2h_structured_payload is not None
    assert calculate_country_h2h_payload is not None
    assert calculate_home_dominance_payload is not None
    assert calculate_away_performance_payload is not None
    assert calculate_global_performance_payload is not None
    assert calculate_continent_performance_payload is not None
    assert calculate_team_form_payload is not None


def test_matchup_package_types_export() -> None:
    assert GlobalH2HContext is not None
    assert CountryH2HContext is not None
    assert HomeDominanceContext is not None
    assert AwayPerformanceContext is not None
    assert GlobalPerformanceContext is not None
    assert ContinentPerformanceContext is not None
    assert TeamFormContext is not None
    assert ComparisonRowsPayload is not None
    assert VenueMatchupPayload is not None
    assert GlobalH2HStructuredPayload is not None
    assert MatrixRowsPayload is not None
    assert TeamFormRowsPayload is not None
    assert ContinentRowsPayload is not None
