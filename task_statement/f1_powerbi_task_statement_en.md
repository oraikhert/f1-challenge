# Late Pace Conversion

## 1. Analysis Context

A Formula 1 team needs to understand whether a driver's pace change relative to the rest of the field during a race is connected to how their position changes from start to finish. The analysis should show not only whether a driver gained or lost positions, but also whether that outcome was accompanied by an improvement in relative pace during the late race phase.

The dashboard is intended for analytical discussion: it should help the team understand whether late-race pace is one of the signals of successful positional progression, or whether position changes are more often explained by other factors.

The main focus of the analysis is not only to identify who gained positions, but to determine whether those drivers had a measurable performance signal: improved relative pace in the final part of the race distance.

## 2. Fundamental Question

How is a driver's change in relative pace during the race connected to their position change from start to finish?

## 3. Testable Hypothesis

**Drivers who improve their relative pace in the late race phase are more likely to gain positions by the finish.**

Russian version:

**Пилоты, улучшающие относительный темп в поздней фазе гонки, чаще отыгрывают позиции к финишу.**

Practical question for the team:

**Can late-race pace improvement be used as an indicator that a driver is capable of attacking or gaining positions in the final part of the race?**

## 4. Data Period and Coverage

The race_ID numbering in the dataset is a technical identifier and does not reflect the chronological order of races. Therefore, the analysis period is defined by the year, round, and race_date fields from races.csv, not by the minimum and maximum race_ID.

The analysis period is limited to races for which both race results and lap times are available:
- start of the period in lap_times.csv: Australian Grand Prix 1996, race date 10.03.1996;
- end of the period in the current lap_times.csv extract: Japanese Grand Prix 2026, race date 29.03.2026;
- level of analysis: one observation is a "driver in a specific race";
- pace granularity: lap times by driver and race.

Races from 1950 to 1995 are excluded from the analysis because the current dataset does not contain lap time data for them. Without lap_times.csv, it is not possible to calculate relative pace by race phase, so these seasons are not used either in hypothesis testing or in dashboard visualizations.dashboard visualizations.

## 5. Unit of Analysis

The main unit of analysis is:

**A driver in a specific race.**

One row in the final analytical table should describe one driver's performance in one race and include:

- race;
- season;
- driver;
- team / constructor;
- starting position;
- finishing position;
- position change from start to finish;
- relative pace in the middle race phase;
- relative pace in the late race phase;
- late pace change relative to the middle phase.

## 6. Core Definitions

### Position Gain

`Position Gain` shows how many positions a driver gained or lost from start to finish.

```text
Position Gain = Start Position - Finish Position
```

Interpretation:

- `Position Gain > 0` — the driver gained positions;
- `Position Gain = 0` — the driver held position;
- `Position Gain < 0` — the driver lost positions.

### Relative Pace %

`Relative Pace %` shows a driver's pace relative to the median field pace in the same race and race phase.

Interpretation:

- negative value — the driver is faster than the field median;
- positive value — the driver is slower than the field median.

### Middle Phase

The middle race phase is used as the baseline pace level. It represents a more stable part of the race than the starting phase, where the first lap, close battles, and start dynamics have a stronger influence.

### Late Phase

The late race phase is used to evaluate whether a driver becomes stronger or weaker relative to the field closer to the finish.

### Late vs Middle Pace Improvement

This metric shows whether a driver improved their relative pace in the late phase compared with the middle phase.

Recommended formula:

```text
Late vs Middle Pace Improvement = Middle Relative Pace % - Late Relative Pace %
```

Interpretation:

- positive value — the driver improved relative pace in the late phase;
- value around zero — pace remained broadly stable;
- negative value — the driver worsened relative pace in the late phase.

This sign convention is chosen for easy interpretation: **higher = better**.

## 7. Main Analytical Groups

### Late Pace Group

Drivers are divided into two main groups:

```text
Late Pace Improved = Late vs Middle Pace Improvement > 0
Late Pace Did Not Improve = Late vs Middle Pace Improvement <= 0
```

### Position Outcome

Drivers are also grouped by position outcome:

```text
Gained Positions = Position Gain > 0
Held Position = Position Gain = 0
Lost Positions = Position Gain < 0
```

## 8. Main Dashboard KPIs

The dashboard should focus on a small set of metrics that directly answer the hypothesis.

### 1. Conversion Rate

The share of drivers who gained positions among those who improved late pace.

```text
Conversion Rate = % of drivers with Position Gain > 0 among drivers with Late vs Middle Pace Improvement > 0
```

This is the primary KPI for the hypothesis.

### 2. Median Position Gain — Late Pace Improvers

Median position change among drivers who improved late pace.

### 3. Median Position Gain — Non-Improvers

Median position change among drivers who did not improve late pace.

### 4. Position Gain Difference

The difference between median `Position Gain` for drivers with and without late pace improvement.

```text
Position Gain Difference = Median Position Gain of Improvers - Median Position Gain of Non-Improvers
```

### 5. Correlation

Rank correlation between `Late vs Middle Pace Improvement` and `Position Gain`.

This metric is useful as additional evidence of the direction of the relationship, but it should not be the main storytelling element.

## 9. Hypothesis Testing Logic

The hypothesis is considered supported if the main conditions are met:

1. Drivers with late pace improvement have a higher `Conversion Rate` than drivers without improvement.
2. Median `Position Gain` is higher for drivers with late pace improvement than for drivers without improvement.
3. There is a positive relationship between `Late vs Middle Pace Improvement` and `Position Gain`.
4. The result is visible in at least some key segments: starting position group, team / constructor, season, or race.

The hypothesis is considered partially supported if the overall effect exists but strongly depends on context, for example if it works only for midfield starters or only for specific teams.

The hypothesis is not considered supported if drivers with late pace improvement do not gain positions more often than others, and if median `Position Gain` is not materially different between the groups.

## 10. Recommended Power BI Report Structure

The report should be short and designed for a presentation of no more than 5 minutes. The optimal structure is 3 pages.

### Page 1 — Executive Verdict

Page objective: immediately show whether the hypothesis is supported.

Recommended elements:

- `Conversion Rate` card;
- `Median Position Gain — Late Pace Improvers` card;
- `Median Position Gain — Non-Improvers` card;
- `Position Gain Difference` card;
- `Position Outcome Share by Late Pace Group` visual;
- short verdict text: supported, partially supported, or not supported.

Main question of the page:

**Do drivers with late pace improvement gain positions more often?**

### Page 2 — Evidence & Relationship

Page objective: show the shape of the relationship between pace improvement and position change.

Recommended elements:

- scatter plot:
  - X-axis: `Late vs Middle Pace Improvement`;
  - Y-axis: `Position Gain`;
  - each point: driver in a race;
  - color: `Position Outcome`;
- bar chart: `Median Position Gain by Late Pace Improvement Bucket`;
- table:
  - pace improvement bucket;
  - number of observations;
  - median `Position Gain`;
  - `% Gained Positions`.

Main question of the page:

**The stronger the late pace improvement, the better the positional outcome?**

### Page 3 — Strategic Application

Page objective: show where the hypothesis is most useful for the team.

Recommended elements:

- `Conversion Rate by Starting Position Group`;
- driver or constructor ranking by:
  - `Late vs Middle Pace Improvement`;
  - `Conversion Rate`;
  - `Median Position Gain`;
- 2x2 matrix:
  - Late Pace Improved / Did Not Improve;
  - Gained Positions / Did Not Gain Positions;
- `Unconverted Late Pace` case table.

Main question of the page:

**Where does late pace improvement actually convert into positions, and where does pace remain unused?**

## 11. 2x2 Conversion Framework

For practical interpretation, the report should use a simple 2x2 matrix.

```text
                         Position Gain
                  Yes                     No

Late Pace     Successful              Unconverted
Improved      Conversion              Late Pace

Late Pace     External /              Expected
Not Improved  Non-Pace Gain           Weakness
```

Interpretation:

### Successful Conversion

The driver improved late pace and gained positions. This is the main positive scenario for the hypothesis.

### Unconverted Late Pace

The driver improved late pace but did not gain positions. This is one of the most important scenarios for the team because it may indicate an execution problem: traffic, poor pit window, lack of track position, or an attack that came too late.

### External / Non-Pace Gain

The driver gained positions without improving late pace. These cases should be interpreted carefully: the position result may have been driven by factors other than late pace.

### Expected Weakness

The driver did not improve late pace and did not gain positions. This is the expected weak scenario.

## 12. Practical Value for the Team

The dashboard should help the team use late-race pace improvement as a simple indicator of strategic opportunity.

If late pace improvement is connected to position gain, the team can consider it a signal for:

- a more aggressive attack in the final race phase;
- planning a longer stint;
- using tyre offset;
- evaluating overcut potential;
- deciding when it is worth saving tyres for a late-race attack.

If late pace improved but positions were not gained, those cases should be reviewed separately. They may show that pace existed, but the team failed to convert it into a result.

## 13. Analysis Limitations

The analysis does not prove a causal relationship between late pace and position gain. It shows whether there is a stable association between the two variables.

Position change may be affected by factors that are not always available in the dataset:

- pit stop strategy;
- traffic;
- DRS train;
- Safety Car and Virtual Safety Car;
- weather;
- tyre degradation;
- car damage;
- penalties;
- retirements of other drivers;
- team tactics.

Therefore, the conclusion should be phrased carefully: late pace improvement may be an indicator of successful positional progression, but it is not necessarily the only cause of that progression.

## 14. Expected Outcome

The final Power BI report should provide a simple answer:

**Are drivers with improved late-race pace more likely to gain positions by the finish?**

Additionally, the report should show:

- how strong the relationship is;
- in which starting position groups it is more visible;
- which drivers or teams convert late pace into positions more effectively;
- where there are cases of unused late pace.

The main value of the report is not a large number of charts, but a short and convincing proof of one hypothesis: **late-race pace improvement can be a practical signal for assessing attack potential and positional progression in the final part of the race.**
