import csv
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "Dataset"
OUT = ROOT / "PowerBI" / "prepared"


def read_csv(name):
    with (DATASET / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def int_or_none(value):
    if value in ("", r"\N", None):
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def float_or_zero(value):
    if value in ("", r"\N", None):
        return 0.0
    return float(value)


def qualifying_stage(row):
    if not row["q1_time"]:
        return "No qualifying data"
    if not row["q2_time"]:
        return "Eliminated Q1"
    if not row["q3_time"]:
        return "Eliminated Q2"
    return "Reached Q3"


def start_group(starting_position):
    pos = int_or_none(starting_position)
    if pos is None:
        return "Unknown"
    if pos == 1:
        return "P1"
    if pos <= 3:
        return "P2-P3"
    if pos <= 10:
        return "P4-P10"
    return "P11+"


def start_group_sort(group):
    return {"P1": 1, "P2-P3": 2, "P4-P10": 3, "P11+": 4, "Unknown": 5}[group]


def issue_category(status):
    if status.startswith("Finished") or status.startswith("+"):
        return "Classified finish"
    if status in {"Accident", "Collision", "Spun off"}:
        return "Driver / incident"
    if status in {
        "Engine",
        "Gearbox",
        "Transmission",
        "Electrical",
        "Hydraulics",
        "Power Unit",
        "Fuel system",
        "Mechanical",
        "Suspension",
        "Battery",
        "Water pressure",
    }:
        return "Technical issue"
    if status in {"Did not qualify", "Did not prequalify", "Withdrew"}:
        return "Did not start / qualify"
    return "Other issue"


drivers = read_csv("drivers.csv")
constructors = read_csv("constructors.csv")
races = read_csv("races.csv")
results = read_csv("results.csv")
lap_times = read_csv("lap_times.csv")
driver_standings = read_csv("driver_standings.csv")
constructor_standings = read_csv("cons_standings.csv")

driver_by_id = {row["driver_ID"]: row for row in drivers}
constructor_by_id = {row["constructor_ID"]: row for row in constructors}
race_by_id = {row["race_ID"]: row for row in races}

result_constructor = {}
for row in results:
    result_constructor[(row["race_ID"], row["driver_ID"])] = row["constructor_ID"]

race_result_counts = Counter(row["race_ID"] for row in results)

dim_races = []
for row in races:
    year = int_or_none(row["year"])
    race_name = row["circuit_name"]
    dim_races.append(
        {
            **row,
            "race_label": f"{row['year']} R{row['round']} - {race_name}",
            "is_miami": 1 if race_name == "Miami Grand Prix" else 0,
            "is_modern_completed_era": 1 if year is not None and 2014 <= year <= 2025 else 0,
            "has_results": 1 if race_result_counts[row["race_ID"]] > 0 else 0,
        }
    )

write_csv(
    OUT / "dim_races.csv",
    dim_races,
    list(dim_races[0].keys()),
)
write_csv(OUT / "dim_drivers.csv", drivers, list(drivers[0].keys()))
write_csv(OUT / "dim_constructors.csv", constructors, list(constructors[0].keys()))

enriched_results = []
for row in results:
    race = race_by_id[row["race_ID"]]
    driver = driver_by_id[row["driver_ID"]]
    constructor = constructor_by_id[row["constructor_ID"]]
    year = int_or_none(race["year"])
    start = int_or_none(row["starting_position"])
    finish = int_or_none(row["race_position"])
    stage = qualifying_stage(row)
    bucket = start_group(row["starting_position"])
    classified = row["status"].startswith("Finished") or row["status"].startswith("+")
    position_delta = "" if start is None or finish is None else start - finish

    enriched_results.append(
        {
            **row,
            "year": race["year"],
            "round": race["round"],
            "circuit_name": race["circuit_name"],
            "circuit_location": race["circuit_location"],
            "circuit_country": race["circuit_country"],
            "constructor_name": constructor["constructor_name"],
            "constructor_ref": constructor["constructor_ref"],
            "driver_name": f"{driver['driver_forename']} {driver['driver_surname']}",
            "driver_code": driver["driver_code"],
            "qualifying_stage": stage,
            "qualifying_stage_rank": {
                "No qualifying data": 0,
                "Eliminated Q1": 1,
                "Eliminated Q2": 2,
                "Reached Q3": 3,
            }[stage],
            "has_qualifying_data": 1 if row["q1_time"] else 0,
            "reached_q3": 1 if stage == "Reached Q3" else 0,
            "start_group": bucket,
            "start_group_sort": start_group_sort(bucket),
            "is_win": 1 if finish == 1 else 0,
            "is_podium": 1 if finish is not None and finish <= 3 else 0,
            "is_points_finish": 1 if float_or_zero(row["points"]) > 0 else 0,
            "is_classified_finish": 1 if classified else 0,
            "is_issue": 0 if classified else 1,
            "issue_category": issue_category(row["status"]),
            "position_change": position_delta,
            "is_mclaren": 1 if constructor["constructor_name"] == "McLaren" else 0,
            "is_miami": 1 if race["circuit_name"] == "Miami Grand Prix" else 0,
            "is_modern_completed_era": 1 if year is not None and 2014 <= year <= 2025 else 0,
            "is_2026_current_form": 1 if year == 2026 and int_or_none(race["round"]) is not None and int(race["round"]) <= 3 else 0,
        }
    )

write_csv(OUT / "fct_results_enriched.csv", enriched_results, list(enriched_results[0].keys()))

team_race = defaultdict(
    lambda: {
        "entries": 0,
        "points": 0.0,
        "starts": [],
        "finishes": [],
        "position_changes": [],
        "q3_starts": 0,
        "issues": 0,
        "podiums": 0,
        "wins": 0,
    }
)
for row in enriched_results:
    key = (row["race_ID"], row["constructor_ID"])
    stats = team_race[key]
    stats["entries"] += 1
    stats["points"] += float_or_zero(row["points"])
    start = int_or_none(row["starting_position"])
    finish = int_or_none(row["race_position"])
    if start is not None:
        stats["starts"].append(start)
    if finish is not None:
        stats["finishes"].append(finish)
    if row["position_change"] != "":
        stats["position_changes"].append(int(row["position_change"]))
    stats["q3_starts"] += int(row["reached_q3"])
    stats["issues"] += int(row["is_issue"])
    stats["podiums"] += int(row["is_podium"])
    stats["wins"] += int(row["is_win"])


def avg(values):
    return "" if not values else round(sum(values) / len(values), 4)


team_race_rows = []
for (race_id, constructor_id), stats in team_race.items():
    race = race_by_id[race_id]
    constructor = constructor_by_id[constructor_id]
    entries = stats["entries"]
    team_race_rows.append(
        {
            "race_ID": race_id,
            "constructor_ID": constructor_id,
            "year": race["year"],
            "round": race["round"],
            "circuit_name": race["circuit_name"],
            "constructor_name": constructor["constructor_name"],
            "entries": entries,
            "points": round(stats["points"], 4),
            "avg_starting_position": avg(stats["starts"]),
            "avg_finish_position": avg(stats["finishes"]),
            "avg_position_change": avg(stats["position_changes"]),
            "q3_starts": stats["q3_starts"],
            "q3_rate": round(stats["q3_starts"] / entries, 4),
            "issues": stats["issues"],
            "issue_rate": round(stats["issues"] / entries, 4),
            "podiums": stats["podiums"],
            "wins": stats["wins"],
            "is_miami": 1 if race["circuit_name"] == "Miami Grand Prix" else 0,
            "is_mclaren": 1 if constructor["constructor_name"] == "McLaren" else 0,
            "is_2026_current_form": 1 if race["year"] == "2026" and int(race["round"]) <= 3 else 0,
        }
    )

write_csv(OUT / "team_race_summary.csv", team_race_rows, list(team_race_rows[0].keys()))

final_constructor_position = {}
for row in constructor_standings:
    race = race_by_id.get(row["race_ID"])
    if not race or not row["cumul_position"]:
        continue
    year = race["year"]
    current = final_constructor_position.get((year, row["constructor_ID"]))
    if current is None or int(race["round"]) > current["round"]:
        final_constructor_position[(year, row["constructor_ID"])] = {
            "round": int(race["round"]),
            "position": row["cumul_position"],
            "points": row["cumul_points"],
        }

team_season = defaultdict(
    lambda: {
        "entries": 0,
        "races": set(),
        "points": 0.0,
        "starts": [],
        "finishes": [],
        "position_changes": [],
        "q3_starts": 0,
        "issues": 0,
        "podiums": 0,
        "wins": 0,
    }
)
for row in enriched_results:
    key = (row["year"], row["constructor_ID"])
    stats = team_season[key]
    stats["entries"] += 1
    stats["races"].add(row["race_ID"])
    stats["points"] += float_or_zero(row["points"])
    start = int_or_none(row["starting_position"])
    finish = int_or_none(row["race_position"])
    if start is not None:
        stats["starts"].append(start)
    if finish is not None:
        stats["finishes"].append(finish)
    if row["position_change"] != "":
        stats["position_changes"].append(int(row["position_change"]))
    stats["q3_starts"] += int(row["reached_q3"])
    stats["issues"] += int(row["is_issue"])
    stats["podiums"] += int(row["is_podium"])
    stats["wins"] += int(row["is_win"])

team_season_rows = []
for (year, constructor_id), stats in team_season.items():
    constructor = constructor_by_id[constructor_id]
    entries = stats["entries"]
    final = final_constructor_position.get((year, constructor_id), {})
    team_season_rows.append(
        {
            "year": year,
            "constructor_ID": constructor_id,
            "constructor_name": constructor["constructor_name"],
            "entries": entries,
            "races": len(stats["races"]),
            "points": round(stats["points"], 4),
            "points_per_race": round(stats["points"] / len(stats["races"]), 4) if stats["races"] else "",
            "avg_starting_position": avg(stats["starts"]),
            "avg_finish_position": avg(stats["finishes"]),
            "avg_position_change": avg(stats["position_changes"]),
            "q3_starts": stats["q3_starts"],
            "q3_rate": round(stats["q3_starts"] / entries, 4),
            "issues": stats["issues"],
            "issue_rate": round(stats["issues"] / entries, 4),
            "podiums": stats["podiums"],
            "wins": stats["wins"],
            "final_constructor_position": final.get("position", ""),
            "final_constructor_points": final.get("points", ""),
            "is_mclaren": 1 if constructor["constructor_name"] == "McLaren" else 0,
        }
    )

write_csv(OUT / "team_season_summary.csv", team_season_rows, list(team_season_rows[0].keys()))

baseline_rows = []
for start_bucket in ["P1", "P2-P3", "P4-P10", "P11+"]:
    bucket_rows = [
        row
        for row in enriched_results
        if row["is_modern_completed_era"] == 1 and row["start_group"] == start_bucket
    ]
    starts = len(bucket_rows)
    podiums = sum(int(row["is_podium"]) for row in bucket_rows)
    wins = sum(int(row["is_win"]) for row in bucket_rows)
    baseline_rows.append(
        {
            "era": "Modern completed era 2014-2025",
            "start_group": start_bucket,
            "start_group_sort": start_group_sort(start_bucket),
            "starts": starts,
            "podiums": podiums,
            "wins": wins,
            "podium_rate": round(podiums / starts, 4) if starts else "",
            "win_rate": round(wins / starts, 4) if starts else "",
        }
    )

write_csv(OUT / "start_group_baseline.csv", baseline_rows, list(baseline_rows[0].keys()))

race_to_year = {row["race_ID"]: row["year"] for row in races}
race_counts = Counter(row["year"] for row in races if race_result_counts[row["race_ID"]] > 0)
season_winners = defaultdict(set)
season_podiums = defaultdict(set)
constructor_wins = defaultdict(Counter)
for row in enriched_results:
    if int(row["is_win"]):
        season_winners[row["year"]].add(row["driver_ID"])
        constructor_wins[row["year"]][row["constructor_ID"]] += 1
    if int(row["is_podium"]):
        season_podiums[row["year"]].add(row["driver_ID"])

competitiveness_rows = []
for year in sorted(season_winners, key=int):
    races_with_results = race_counts[year]
    top_constructor_wins = max(constructor_wins[year].values()) if constructor_wins[year] else 0
    competitiveness_rows.append(
        {
            "year": year,
            "races": races_with_results,
            "distinct_winners": len(season_winners[year]),
            "distinct_podium_finishers": len(season_podiums[year]),
            "winner_share": round(len(season_winners[year]) / races_with_results, 4) if races_with_results else "",
            "podium_share": round(len(season_podiums[year]) / races_with_results, 4) if races_with_results else "",
            "top_constructor_win_share": round(top_constructor_wins / races_with_results, 4) if races_with_results else "",
        }
    )

write_csv(OUT / "season_competitiveness.csv", competitiveness_rows, list(competitiveness_rows[0].keys()))

lap_groups = defaultdict(list)
for row in lap_times:
    constructor_id = result_constructor.get((row["race_ID"], row["driver_ID"]))
    if constructor_id is None:
        continue
    lap_ms = int_or_none(row["lap_time_ms"])
    if lap_ms is None:
        continue
    lap_groups[(row["race_ID"], constructor_id)].append(lap_ms)

lap_summary_rows = []
for (race_id, constructor_id), laps in lap_groups.items():
    race = race_by_id[race_id]
    constructor = constructor_by_id[constructor_id]
    lap_summary_rows.append(
        {
            "race_ID": race_id,
            "constructor_ID": constructor_id,
            "year": race["year"],
            "round": race["round"],
            "circuit_name": race["circuit_name"],
            "constructor_name": constructor["constructor_name"],
            "lap_count": len(laps),
            "median_lap_time_ms": int(statistics.median(laps)),
            "avg_lap_time_ms": round(sum(laps) / len(laps), 2),
            "best_lap_time_ms": min(laps),
            "is_miami": 1 if race["circuit_name"] == "Miami Grand Prix" else 0,
            "is_mclaren": 1 if constructor["constructor_name"] == "McLaren" else 0,
        }
    )

write_csv(OUT / "team_race_lap_summary.csv", lap_summary_rows, list(lap_summary_rows[0].keys()))

print(f"Prepared Power BI files written to {OUT}")
