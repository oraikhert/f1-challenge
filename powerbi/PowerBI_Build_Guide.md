# McLaren Miami GP Power BI Dashboard Build Guide

## 1. Objective

Build a Power BI report that answers one clear question:

```text
What is the main performance risk McLaren must control to fight for a podium or win in Miami?
```

Main hypothesis:

```text
McLaren's key risk before Miami is not qualifying pace, but race conversion. The team has shown enough qualifying strength to compete near the front, but reliability and race execution issues can prevent that pace from becoming points, podiums, or wins.
```

Use the general F1 grid-position analysis only as an analytical baseline, not as a second hypothesis.

## 2. Prepared Files

Use the prepared CSV files in:

```text
PowerBI/prepared/
```

Import these files into Power BI:

| File | Rename table to | Purpose |
|---|---|---|
| `fct_results_enriched.csv` | `Results` | Main fact table, one row per driver race result |
| `dim_races.csv` | `Races` | Race/circuit/calendar attributes |
| `dim_drivers.csv` | `Drivers` | Driver attributes |
| `dim_constructors.csv` | `Constructors` | Constructor/team attributes |
| `team_race_summary.csv` | `Team Race Summary` | Team-level race summary |
| `team_season_summary.csv` | `Team Season Summary` | Team-level season summary |
| `start_group_baseline.csv` | `Start Group Baseline` | Pre-aggregated modern F1 starting-position baseline |
| `season_competitiveness.csv` | `Season Competitiveness` | Optional background trend table |
| `team_race_lap_summary.csv` | `Team Race Lap Summary` | Team-level lap pace summary |

## 3. Import Steps

1. Open Power BI Desktop.
2. Select `Get Data` > `Text/CSV`.
3. Import all CSV files from `PowerBI/prepared/`.
4. Rename the tables exactly as listed above.
5. Open `Transform Data`.
6. Check data types:
   - IDs: whole number or text is acceptable, but keep the same type across related tables.
   - `year`, `round`, positions, flags: whole number.
   - `points`, rates, average positions, lap times: decimal number.
   - `race_date`, `quali_date`: date if Power BI parses them correctly; otherwise leave as text.
7. Close and apply.

## 4. Model Relationships

Create these relationships in Model view:

| From | To | Cardinality | Direction |
|---|---|---|---|
| `Races[race_ID]` | `Results[race_ID]` | One to many | Single |
| `Constructors[constructor_ID]` | `Results[constructor_ID]` | One to many | Single |
| `Drivers[driver_ID]` | `Results[driver_ID]` | One to many | Single |
| `Races[race_ID]` | `Team Race Summary[race_ID]` | One to many | Single |
| `Constructors[constructor_ID]` | `Team Race Summary[constructor_ID]` | One to many | Single |
| `Races[race_ID]` | `Team Race Lap Summary[race_ID]` | One to many | Single |
| `Constructors[constructor_ID]` | `Team Race Lap Summary[constructor_ID]` | One to many | Single |
| `Constructors[constructor_ID]` | `Team Season Summary[constructor_ID]` | One to many | Single |

Do not create unnecessary many-to-many relationships. If Power BI auto-created relationships you do not need, remove them.

Sort fields:

1. Select `Results[start_group]`, then `Sort by column` = `Results[start_group_sort]`.
2. Select `Start Group Baseline[start_group]`, then `Sort by column` = `Start Group Baseline[start_group_sort]`.
3. Select `Results[qualifying_stage]`, then `Sort by column` = `Results[qualifying_stage_rank]`.

## 5. Measures

Create a blank table called `Measures`:

1. Home > Enter Data.
2. Add one column called `Name`.
3. Add one row with value `Measures`.
4. Load.
5. Hide the `Name` column.

Then create the measures from:

```text
PowerBI/dax_measures.dax
```

If your Power BI locale requires semicolon separators, replace commas in DAX functions with semicolons.

Format these measures as percentages:

```text
Podium Rate
Win Rate
Points Finish Rate
Issue Rate
Q3 Rate
Top 3 Start Podium Rate
McLaren Q3 Rate
McLaren Issue Rate
Current Form Q3 Rate
Current Form Issue Rate
```

## 6. Report Theme

Use a clean motorsport style:

| Element | Color |
|---|---|
| Background | `#F6F6F3` |
| Text | `#111111` |
| McLaren highlight | `#FF8000` |
| Benchmark dark | `#1E1E1E` |
| Ferrari comparison | `#DC0000` |
| Mercedes comparison | `#00A19C` |
| Red Bull comparison | `#1E41FF` |
| Neutral grey | `#B8B8B8` |

Recommended report settings:

- Page size: `16:9`.
- Use one main question per page.
- Put slicers consistently at the top or left.
- Keep visual titles short and assertive.
- Use orange only for McLaren highlights, not for every visual.

## 7. Page 1: Executive Summary

Page title:

```text
McLaren Miami Readiness: Pace Is There, Conversion Is The Risk
```

Purpose:

Give the judging panel the answer in the first 20 seconds.

Filters:

- Use measure-level filters for McLaren where possible.
- For current form visuals, filter `Results[is_2026_current_form] = 1`.

Visuals:

1. Card: `McLaren Q3 Rate`
   - Visual filter: `Results[is_2026_current_form] = 1`
   - Expected message: McLaren is reaching Q3 consistently.

2. Card: `McLaren Average Start`
   - Visual filter: `Results[is_2026_current_form] = 1`

3. Card: `McLaren Average Finish`
   - Visual filter: `Results[is_2026_current_form] = 1`

4. Card: `McLaren Issue Rate`
   - Visual filter: `Results[is_2026_current_form] = 1`

5. Card: `McLaren Miami Wins`
   - Visual filter: `Results[year] <= 2025`

6. Scatter chart: `2026 Team Risk Map`
   - Table: `Team Race Summary`
   - Filter: `is_2026_current_form = 1`
   - X-axis: `avg_starting_position`
   - Y-axis: `issue_rate`
   - Size: `points`
   - Details/Legend: `constructor_name`
   - Interpretation: lower X is better; lower Y is safer. McLaren should appear as fast but risky.

7. Text box insight:

```text
McLaren's Miami opportunity is real because the team has qualifying pace and recent Miami wins. The risk is conversion: 2026 results show strong grid performance but unstable race outcomes.
```

## 8. Page 2: F1 Baseline - Why Grid Position Matters

Page title:

```text
Modern F1 Baseline: Track Position Shapes Race Outcomes
```

Purpose:

Establish the analytical baseline. Do not call this the main hypothesis.

Filters:

- Use `Start Group Baseline` table, already limited to `2014-2025`.

Visuals:

1. Clustered column chart: `Podium and Win Rate by Start Group`
   - Axis: `Start Group Baseline[start_group]`
   - Values: `podium_rate`, `win_rate`
   - Format as percentage.

2. Line chart: `Average Finish by Starting Position`
   - Table: `Results`
   - Filter: `is_modern_completed_era = 1`
   - X-axis: `starting_position`
   - Y-axis: `Average Finish`
   - Visual filter: `starting_position <= 20`

3. Matrix: `Baseline Summary`
   - Rows: `Start Group Baseline[start_group]`
   - Values: `starts`, `podiums`, `wins`, `podium_rate`, `win_rate`

4. Text box insight:

```text
Starting near the front materially changes the probability of reaching the podium. This explains why McLaren's Q3 strength matters before Miami.
```

## 9. Page 3: McLaren Diagnosis

Page title:

```text
McLaren Diagnosis: Qualifying Strength, Race Conversion Risk
```

Purpose:

Test the main hypothesis directly.

Filters:

- Page filter: `Results[constructor_name] = McLaren`
- Recommended slicer: `Results[year]`

Visuals:

1. Stacked column chart: `Qualifying Stage by Year`
   - Axis: `Results[year]`
   - Legend: `Results[qualifying_stage]`
   - Values: `Total Starts`
   - Filter: `year >= 2022`

2. Line chart: `Average Start vs Average Finish`
   - Axis: `Team Season Summary[year]`
   - Values: `avg_starting_position`, `avg_finish_position`
   - Filter: `Team Season Summary[constructor_name] = McLaren`
   - Filter: `year >= 2022`

3. Column chart: `Issue Rate by Season`
   - Axis: `Team Season Summary[year]`
   - Values: `issue_rate`
   - Filter: `constructor_name = McLaren`
   - Filter: `year >= 2022`

4. Table: `2026 Problem Races`
   - Table: `Results`
   - Filter: `constructor_name = McLaren`
   - Filter: `is_2026_current_form = 1`
   - Columns: `circuit_name`, `driver_name`, `qualifying_stage`, `starting_position`, `race_position`, `points`, `status`, `issue_category`

5. Text box insight:

```text
In 2026 McLaren's qualifying signal is strong, but race outcomes are volatile. The issue is not getting into the fight; it is finishing the fight cleanly.
```

## 10. Page 4: Miami Readiness

Page title:

```text
Miami Readiness: A Real Opportunity If Execution Is Clean
```

Purpose:

Connect the diagnosis to the upcoming Miami GP.

Filters:

- Page filter: `Results[is_miami] = 1`
- Filter years to `2022-2025` for completed Miami races.

Visuals:

1. Clustered bar chart: `Miami Points by Constructor`
   - Axis: `Results[constructor_name]`
   - Values: `Total Points`
   - Filter constructors to McLaren, Red Bull, Ferrari, Mercedes.

2. Clustered column chart: `Miami Wins and Podiums`
   - Axis: `Results[constructor_name]`
   - Values: `Wins`, `Podiums`
   - Filter constructors to McLaren, Red Bull, Ferrari, Mercedes.

3. Table: `Miami Result Timeline`
   - Columns: `year`, `driver_name`, `constructor_name`, `starting_position`, `race_position`, `points`, `status`
   - Visual filter: `race_position <= 8`
   - Sort by `year`, then `race_position`.

4. Clustered column chart: `Miami Median Lap Time`
   - Table: `Team Race Lap Summary`
   - Filter: `is_miami = 1`
   - Filter: `year IN 2024, 2025`
   - Filter constructors to McLaren, Red Bull, Ferrari, Mercedes.
   - Axis: `constructor_name`
   - Legend: `year`
   - Values: `Median Lap Time sec`

5. Text box insight:

```text
Miami is not a neutral opportunity for McLaren. Recent Miami results and lap pace suggest the team can fight at the front, but the 2026 risk profile makes clean execution decisive.
```

## 11. Page 5: Recommendation

Page title:

```text
Recommendation: Protect The Pace
```

Purpose:

End with clear, practical advice.

Layout:

1. Left side: three recommendation cards.
2. Right side: small supporting KPI strip or mini charts.

Recommendation cards:

```text
1. Prioritize clean Q3-to-race conversion.
McLaren does not need to prove raw pace first; it needs to protect strong grid positions.
```

```text
2. Treat reliability and execution as podium-critical.
Recent 2026 issues show that technical or race execution losses can erase qualifying strength.
```

```text
3. Use Miami as an attack opportunity, not a recovery race.
McLaren's recent Miami record supports a podium/win target if the race is clean.
```

Supporting visuals:

- Card: `McLaren Miami Wins`
- Card: `McLaren Miami Podiums`
- Card: `McLaren Q3 Rate` with 2026 current form filter
- Card: `McLaren Issue Rate` with 2026 current form filter

Final text box:

```text
Conclusion: McLaren's Miami question is not "can the car be fast enough?" The data suggests it can. The question is whether the team can convert that speed into a clean race result.
```

## 12. Video Walkthrough Script

Keep it under 5 minutes.

### 0:00-0:30 - Context

```text
I am analysing McLaren before the Miami GP. The goal is to identify the main performance risk the team must control to fight for a podium or win.
```

### 0:30-1:15 - Baseline

```text
First I establish a modern F1 baseline: starting position strongly shapes race outcome. This is important because it tells us why qualifying strength matters.
```

Show Page 2.

### 1:15-2:25 - McLaren Diagnosis

```text
Then I apply that baseline to McLaren. The team is not lacking qualifying pace: the Q3 signal is strong. But the gap between starting potential and race outcome reveals the risk.
```

Show Page 3.

### 2:25-3:30 - Current Risk

```text
The 2026 current-form data shows instability in race conversion. This means McLaren's main risk before Miami is not raw pace, but reliability and race execution.
```

Show the problem-race table and issue rate.

### 3:30-4:30 - Miami Opportunity

```text
Miami is a real opportunity. Recent Miami results show McLaren can compete at the front here, including wins and strong lap pace.
```

Show Page 4.

### 4:30-5:00 - Recommendation

```text
My recommendation is to protect the pace. McLaren should focus on clean execution from Q3 into the race, because the data suggests the speed is already there.
```

Show Page 5.

## 13. Evaluation Checklist

Quality of hypothesis:

- Use one main hypothesis only.
- Call the grid-position analysis a baseline, not a second hypothesis.
- Keep the business question tied to McLaren and Miami.

Use and understanding of data:

- Explain the `q1_time`, `q2_time`, `q3_time` logic.
- Explain `status` classification: classified finish versus issue.
- Acknowledge that Miami has a small sample, so it is supporting context.

Analytical rigor:

- Use 2014-2025 for modern F1 baseline.
- Use 2026 first three races for current form.
- Use Miami 2022-2025 for track-specific context.
- Avoid claims that require missing data, such as tyres, pit stops, weather, or strategy.

Storytelling:

- Follow this sequence: baseline -> McLaren diagnosis -> Miami opportunity -> recommendation.
- Each page should answer one question.
- Repeat the core message: pace exists, conversion is the risk.

Dashboard design:

- Keep KPI cards consistent.
- Use McLaren orange only to highlight McLaren.
- Use short visual titles that state the point.
- Avoid too many slicers and small tables.
