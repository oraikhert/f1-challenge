# Task Statement for a Power BI Dashboard on Formula 1 Driver Pace Analysis

## 1. Analysis Context

A Formula 1 team needs to understand how a driver's position change from start to finish is related to how their pace changes relative to the rest of the field over the race distance. The analysis should show not only whether a driver gained or lost positions, but also whether this was accompanied by an improvement in relative pace during the late phase of the race.

The dashboard is intended for analytical discussion: it should help the team determine whether late-race pace is one of the indicators of successful position gain, or whether position changes are more often explained by other factors.

## 2. Fundamental Question

How is a driver's position change from start to finish related to the change in their relative pace over the course of the race?

## 3. Testable Hypothesis

Drivers who improve their finishing position relative to their starting position are faster relative to the other drivers in the late phase of the race than they were relative to them in the initial and middle phases.

The hypothesis is considered supported if both of the following patterns are observed in the data:

1. Drivers who gain positions have better relative pace in the late phase of the race than in the initial and middle phases.
2. The group of drivers who gain positions shows a stronger improvement in late relative pace than drivers who maintain or lose positions.

The hypothesis is considered rejected or not supported if the relationship is weak, unstable across seasons/races, or if drivers who gain positions do not show better late relative pace compared with the rest of the field.

## 4. Analysis Period and Data Coverage

The `race_ID` numbering in the dataset is a technical identifier and does not reflect the chronological order of races. Therefore, the period is determined using the `year`, `round`, and `race_date` fields from `races.csv`, rather than the minimum and maximum `race_ID`.

The analysis period is limited to races for which both race results and lap times are available:

- start of the period in `lap_times.csv`: Australian Grand Prix 1996, race date 10.03.1996;
- end of the period in the current `lap_times.csv` extract: Japanese Grand Prix 2026, race date 29.03.2026;
- analysis level: one observation per driver in a specific race;
- pace granularity: lap times by driver and race.

Races from 1950-1995 are excluded from the analysis because the current dataset does not contain lap time data for them. Without `lap_times.csv`, relative pace by race phase cannot be calculated, so these seasons are not used either in hypothesis testing or in dashboard visuals.

## 5. Core Definitions

### Position Change

`Position Gain = Starting Position - Finish Position`

- a positive value means the driver gained positions;
- zero means the driver finished in the same position they started from;
- a negative value means the driver lost positions.

### Race Phases

Each race is divided into three phases based on the lap number relative to the full race distance:

- initial phase: 0-25% of the race distance;
- middle phase: 40-60% of the race distance;
- late phase: 75-100% of the race distance.

The first lap is excluded from the pace calculation because it reflects the start, traffic density, and position battles more strongly than stable race pace.

### Relative Pace

A driver's relative pace in a race phase is calculated as the deviation of the driver's median lap time from the median lap time of all drivers in the same race and the same phase.

Example formula:

`Relative Pace Phase % = Driver Median Lap Time Phase / Field Median Lap Time Phase - 1`

- a value below 0 means the driver was faster than the median field pace;
- a value above 0 means the driver was slower than the median field pace.

### Late Pace Improvement

`Late Pace Improvement = Avg(Relative Pace Initial, Relative Pace Middle) - Relative Pace Late`

Here `Avg` means the arithmetic mean of the two already calculated relative pace values; it does not mean average lap time.

- a positive value means the driver became faster relative to the field in the late phase;
- a negative value means the driver became slower relative to the field in the late phase.

## 6. Metrics for Testing the Hypothesis

1. `Starting Position` - the driver's starting position.
2. `Finish Position` - the driver's finishing position.
3. `Position Gain` - the change in position from start to finish.
4. `Relative Pace Initial %` - relative pace in the initial race phase.
5. `Relative Pace Middle %` - relative pace in the middle race phase.
6. `Relative Pace Late %` - relative pace in the late race phase.
7. `Late Pace Improvement` - improvement in relative pace in the late phase compared with the initial and middle phases.
8. `Driver Race Count` - the number of races in the sample for a driver.
9. `Median Position Gain by Driver/Season` - median position change by driver or season.
10. `Median Late Pace Improvement by Driver/Season` - median late pace improvement by driver or season.
11. `Correlation: Position Gain vs Late Pace Improvement` - the strength of the relationship between positions gained and late pace improvement.
12. `Group Difference` - the difference in median `Late Pace Improvement` between drivers who gained positions and drivers who did not gain positions.

## 7. Comparison Segments

To test the hypothesis, drivers in each race are divided into three groups:

- `Gained Positions`: `Position Gain > 0`;
- `No Change`: `Position Gain = 0`;
- `Lost Positions`: `Position Gain < 0`.

The analysis should also support filtering by:

- season;
- race;
- driver;
- team/constructor;
- starting position;
- finishing position;
- finishing status.

## 8. Analysis Limitations and Simplifications

The analysis focuses on the relationship between position change and the dynamics of relative pace, but it does not claim to provide a complete causal explanation of the race result.

The following factors are simplified or not considered in this task statement:

1. Pit stops are not modeled separately if the dataset does not contain explicit pit stop data.
2. Tires, tire compounds, degradation, tire age, and strategy are not included directly.
3. Safety Car, Virtual Safety Car, red flags, and neutralization periods are not identified as separate events.
4. Weather conditions, wet track conditions, and track evolution are not included as separate features.
5. Traffic, DRS, slipstream, and wheel-to-wheel battles are not modeled directly.
6. Technical issues, penalties, and damage are captured only indirectly through final position, status, and lap times.
7. Very slow laps may still distort interpretation, but median-based pace indicators are used to reduce their influence; extreme outliers should still be reviewed.
8. Drivers who do not have enough laps in all three race phases may be excluded from phase pace calculations.
9. Races from 1950-1995 are excluded from the analysis because the current extract does not contain `lap_times.csv` data required to calculate phase-based relative pace.

## 9. Power BI Dashboard Structure

### Page 1. Executive Summary: Hypothesis Answer

The goal of this page is to provide a quick answer on whether the hypothesis is supported at the aggregate level.

Planned elements:

- KPI: number of races, number of driver-race observations, average `Position Gain`, median `Late Pace Improvement`;
- KPI or card showing the direction of the relationship between `Position Gain` and `Late Pace Improvement`;
- scatter plot: `Position Gain` on the X-axis and `Late Pace Improvement` on the Y-axis;
- color split by `Gained Positions`, `No Change`, and `Lost Positions`;
- bar chart: median `Late Pace Improvement` across the three position-change groups;
- filters by season, race, driver, and constructor;
- text block with the current verdict: "hypothesis supported", "not supported", or "requires further clarification".

### Page 2. Race Phase Pace: How Pace Changes Across Phases

The goal of this page is to show whether the pace profiles of drivers who gained positions differ from those of drivers who lost positions.

Planned elements:

- line chart: median relative pace by race phase for the `Gained Positions`, `No Change`, and `Lost Positions` groups;
- matrix/heatmap: drivers or teams as rows, race phases as columns, and relative pace as the value;
- bar chart: difference between late relative pace and the mean of the initial/middle relative pace values;
- filters by season, race, team, and finishing status.

### Page 3. Driver and Race Drilldown: Driver or Race Breakdown

The goal of this page is to allow the team to validate the aggregate finding through specific examples.

Planned elements:

- table of drivers in the selected race: start, finish, `Position Gain`, relative pace by phase, and `Late Pace Improvement`;
- lap-by-lap line chart: driver's position on each lap;
- lap-by-lap line chart: lap time or relative lap pace;
- comparison of the selected driver against the field median;
- ability to select one or multiple drivers for comparison.

### Page 4. Season and Constructor View: Effect Stability

The goal of this page is to check whether the relationship remains stable across seasons and teams, rather than being driven by a few individual races.

Planned elements:

- trend chart: correlation between `Position Gain` and `Late Pace Improvement` by season;
- bar chart: median `Late Pace Improvement` by constructor;
- scatter plot by season or team;
- season table with the number of observations, median `Position Gain`, median `Late Pace Improvement`, and relationship direction.

## 10. Five-Minute Presentation Storyline

1. Minute 1: state the question - does position gain come from real pace at the end of the race, or from other race circumstances?
2. Minute 2: explain the method - split the race into initial, middle, and late phases, calculate median-based relative pace against the field median, and compare it with position change.
3. Minute 3: show the overall result on the Executive Summary page - whether there is a relationship between `Position Gain` and `Late Pace Improvement`.
4. Minute 4: move to Race Phase Pace and show how pace profiles differ between drivers who gained and lost positions.
5. Minute 5: open Driver and Race Drilldown, show one concrete example, then return to the conclusion: the hypothesis is supported, rejected, or requires further clarification.

## 11. Example Conclusion if the Hypothesis Is Supported

If the hypothesis is supported, the final conclusion may be stated as follows:

"In the analyzed period, drivers who gained positions from start to finish were, on average, faster relative to the field in the late phase of the race than in the initial and middle phases. A positive relationship is observed between the number of positions gained and late pace improvement. This means that late-race pace may be one indicator of successful position gain, although by itself it does not prove causality without accounting for strategy, pit stops, tires, and race incidents."

## 12. Example Conclusion if the Hypothesis Is Rejected

If the hypothesis is not supported, the final conclusion may be stated as follows:

"In the analyzed period, no stable relationship was found between improvement in position from start to finish and improvement in relative pace during the late phase of the race. Drivers who gained positions do not systematically demonstrate better late-race pace compared with drivers who maintained or lost positions. This indicates that position change may be explained to a greater extent by start events, strategy, pit stops, retirements of competitors, penalties, or race-specific circumstances."

## 13. Expected Dashboard Outcome

The dashboard should allow the Formula 1 team to:

- quickly see the overall answer to the hypothesis;
- compare driver pace across race phases;
- test the relationship between position outcome and pace dynamics;
- move from an aggregate conclusion to a specific driver or race;
- separate the observed statistical relationship from possible race causes that are not directly represented in the dataset.
