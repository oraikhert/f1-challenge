# Project Brief for a Power BI Dashboard

## Analysis Topic

**McLaren: observed race-pace stability in Miami as a potential competitive advantage over rivals**

---

## 1. Fundamental Question

**Can McLaren gain a competitive advantage at the Miami Grand Prix through more stable observed long-run race pace compared with its main rivals?**

In other words: McLaren does not necessarily need to be the fastest team over a single lap. The analysis should show whether the team can be competitive because its pace deteriorates less over the race distance relative to Ferrari, Mercedes, and Red Bull.

Important: given the available data model, the analysis measures **observed lap-time stability**, not pure tyre degradation or pure car performance. The dataset does not include tyre compound, tyre age, pit-stop timing, weather, DRS, Safety Car, or Virtual Safety Car data. Therefore, all conclusions must be framed with these limitations in mind.

---

## 2. Testable Hypothesis

**Hypothesis:**

In modern races comparable to the Miami Grand Prix, McLaren demonstrates more stable **observed race pace** on clean racing laps than Ferrari, Mercedes, and Red Bull: its relative lap time deteriorates less from the beginning to the end of the race, and its lap-time variability is lower than that of its main competitors.

**What “confirmed” means:**

The hypothesis is considered confirmed if, after filtering obvious lap-time anomalies, McLaren simultaneously:

1. shows a smaller pace drop-off between the first and last parts of the race;
2. has lower lap-time variability;
3. reduces the gap to competitors or increases its advantage over them in the second half of the race;
4. shows this pattern not only in a single Miami race, but also across at least part of the comparable-circuit sample in the modern period.

**What “rejected” means:**

The hypothesis is considered rejected if McLaren does not differ from its competitors in terms of pace stability, if its pace drops off more than Ferrari, Mercedes, or Red Bull, or if the result disappears after excluding anomalous laps.

**What “partially confirmed” means:**

The hypothesis is considered partially confirmed if McLaren appears more stable only on one group of metrics, only in Miami, or only in selected seasons, but does not show a robust advantage in the broader comparison.

---

## 3. Data Limitations and How They Are Addressed

The available data model is well suited for lap-by-lap pace analysis, but it does not include several factors that strongly affect Formula 1 lap times.

| Missing data | How it can bias the analysis | How it is addressed in the dashboard |
|---|---|---|
| **Tyre compound and tyre age** | The analysis cannot directly separate tyre degradation from other causes of slowing down | Do not call the metric “tyre degradation”; use **Observed Pace Drift** instead |
| **Pit stops** | In-laps and out-laps can look like sudden pace losses | Detect and exclude obvious individual lap-time outliers |
| **Weather** | Rain, track temperature, and wind can change the pace of the whole field | Compare teams within the same race and lap using relative pace |
| **DRS** | The analysis cannot explain precisely why a driver accelerated or gained a position | Do not make claims about DRS effectiveness; use position change only as context |
| **Safety Car / VSC** | Race neutralisations sharply increase lap times across the field | Flag potential neutralised laps through field-wide lap-time spikes and exclude them from pace metrics |
| **Traffic and on-track battles** | A driver may be slower because of cars ahead, not because of car pace | Use medians, rolling averages, and race-phase comparison rather than isolated laps |

### Rule for Wording Conclusions

The dashboard must not claim: “McLaren manages tyres better,” because tyre data is not available. The correct wording is: **“McLaren shows more stable observed race pace in the cleaned lap-time data.”**

---

## 4. Metrics for Testing the Hypothesis

### Core Metrics

| Metric | Description | Purpose |
|---|---|---|
| **Average Lap Time** | Team average `lap_time_ms` | Shows overall observed race pace |
| **Median Lap Time** | Team median `lap_time_ms` | More robust to outliers than the average |
| **Relative Pace Delta** | Difference between a driver's or team's lap time and the median lap time of the selected competitor group on the same lap | Enables pace comparison within the same race and lap |
| **Observed Pace Drift** | Difference between median pace in the final and first parts of the race | Main metric for observed pace drop-off |
| **Lap Time Variability** | Standard deviation or IQR of `lap_time_ms` | Measures pace consistency |
| **Late Race Pace** | Average or median pace in the final third of the race | Shows team strength closer to the finish |
| **Late Race Advantage** | Change in `Relative Pace Delta` between the first and final parts of the race | Shows whether McLaren becomes stronger relative to rivals |
| **Clean Lap Share** | Share of laps remaining after anomaly filtering | Indicates sample reliability |
| **Position Change by Race Phase** | Position change by race phase based on `position` from `lap_times` | Helps connect pace to on-track result, but does not prove pace advantage |

---

### Recommended Calculated Metrics

#### 1. Relative Pace Delta

```text
Relative Pace Delta =
Driver or Team Lap Time
-
Median Lap Time of the selected competitor group on the same lap
```

Interpretation:

- negative value — the team is faster than the benchmark;
- positive value — the team is slower than the benchmark;
- value close to zero — pace is approximately in line with competitors.

---

#### 2. Observed Pace Drift

```text
Observed Pace Drift =
Median Clean Lap Time in the final third of the race
-
Median Clean Lap Time in the first third of the race
```

The lower the value, the more stable the team's observed race pace. This metric must not be interpreted as pure tyre degradation.

---

#### 3. Team Consistency Index

```text
Team Consistency Index =
IQR or Standard Deviation of lap_time_ms on clean racing laps
```

The lower the value, the more consistent the team's observed pace.

---

#### 4. Late Race Advantage

```text
Late Race Advantage =
Relative Pace Delta in the final third of the race
-
Relative Pace Delta in the first third of the race
```

If the value improves toward the end of the race, the team becomes relatively stronger over the race distance.

---

#### 5. Potentially Unclean Lap Flag

```text
Potentially Unclean Lap =
Lap is an outlier vs driver's rolling median
OR
Lap is part of a field-wide lap-time spike
```

This metric is not intended as a sporting conclusion. It improves analytical quality by separating regular racing laps from laps potentially distorted by pit stops, Safety Car, VSC, rain, traffic, or other anomalies.

---

## 5. Analysis Period

Recommended period:

**2022–2026, up to the latest completed race before the 2026 Miami Grand Prix.**

Rationale:

- The Miami Grand Prix only appeared in modern Formula 1 history in 2022.
- Older seasons starting from 1950 are not suitable for direct comparison because of different cars, regulations, race formats, tyre rules, and team lineups.
- For an applied team-focused analysis, the modern period is more relevant than the entire historical database.
- Since 2022, Formula 1 has been in the current regulation era, making team comparisons more relevant.

Primary analysis focus:

1. **Miami Grand Prix 2022–2025** — direct historical context for the circuit.
2. **Modern races from 2022–2026** — additional context on current team strength.
3. **Similar circuits** — to expand the sample if Miami alone provides too few observations.

When using 2026 data, only races completed before Miami should be included so that the analysis genuinely reflects preparation for the upcoming weekend.

---

## 6. Comparison with Other Teams

### Main Team for the Analysis

**McLaren**

The project brief is written as if the analyst works inside McLaren and is preparing a dashboard for the Miami race weekend.

---

### Main Competitors for Comparison

| Team | Why compare against them |
|---|---|
| **Red Bull** | Benchmark for strong race pace |
| **Ferrari** | Direct rival for podiums / high points finishes |
| **Mercedes** | Team with potentially strong race pace and strategic execution |
| **Aston Martin** | Additional reference point if broader comparison is needed |
| **Williams / Alpine / Haas** | Not McLaren's primary rivals, but useful for wider midfield context |

---

### Comparison Logic

The comparison should not rely only on absolute lap time. It should be evaluated across three levels:

1. **Absolute observed pace**  
   Which team is faster by average and median lap time.

2. **Pace stability**  
   Which team has lower lap-time variability on clean laps.

3. **Pace evolution during the race**  
   Which team loses less relative pace from the beginning to the end of the race distance.

Main analytical angle:  
**McLaren may not be the fastest team at the beginning of the race, but it may become stronger relative to its competitors in the second half of the race.**

---

## 7. Power BI Dashboard Structure

For a 5-minute story, the optimal structure is **5 pages**: four analytical pages and one page for data limitations / methodology. If a more compact format is required, the methodology page can be hidden or used as a tooltip / appendix.

---

## Page 1 — Executive Summary

**Page objective:**  
Immediately answer whether the hypothesis is supported.

### Main Elements

- KPI card: `McLaren Observed Pace Drift`
- KPI card: `McLaren Consistency Index`
- KPI card: `McLaren Late Race Pace Rank`
- KPI card: `Clean Lap Share`
- Hypothesis status indicator: **Confirmed / Partially Confirmed / Rejected**
- Bar chart: `Observed Pace Drift` comparison by team
- Bar chart: `Lap Time Variability` comparison by team
- Small warning block: “Analysis based on lap time data only; tyre, pit stop, weather, DRS and Safety Car data are not available.”

### Main Question on the Page

**Is McLaren actually more stable than its competitors over a long run in the cleaned lap-time data?**

---

## Page 2 — Race Pace Evolution

**Page objective:**  
Show how team pace changes over the race distance.

### Main Elements

- Line chart: `Relative Pace Delta` by `lap_num`
- Toggle: `Raw laps / Clean laps`
- Filters:
  - season;
  - circuit;
  - team;
  - driver;
  - race.
- McLaren highlighted with a distinct color
- 3-lap or 5-lap rolling average to smooth noise
- Markers for potentially anomalous laps

### Main Question on the Page

**At what point in the race does McLaren become stronger or weaker relative to its competitors?**

---

## Page 3 — Race Phases Comparison

**Page objective:**  
Break the race into clear phases.

### Race Phases

- **Early Race:** first 25% of the distance
- **Mid Race:** 25–75% of the distance
- **Late Race:** final 25% of the distance

### Main Elements

- Clustered bar chart: average `Relative Pace Delta` by race phase
- Matrix: teams × race phases
- Slope chart: pace change from Early Race to Late Race
- Tooltip with McLaren drivers
- Filter: “Include / Exclude potentially unclean laps”

### Main Question on the Page

**Does McLaren's pace drop off less than its competitors from the beginning to the end of the race?**

---

## Page 4 — Miami vs Similar Circuits

**Page objective:**  
Understand whether Miami is a unique circuit or part of a broader pattern.

### Main Elements

- Scatter plot:
  - X-axis: `Average Relative Pace`
  - Y-axis: `Lap Time Variability`
  - points: teams / circuits
- Bar chart: McLaren `Observed Pace Drift` by circuit
- Table: ranking of circuits where McLaren is most stable
- Circuit filter: Miami, Jeddah, Baku, Singapore, Las Vegas, Monaco, and other street / semi-street circuits

### Main Question on the Page

**Is Miami similar to circuits where McLaren has already shown stable observed race pace?**

---

## Page 5 — Data Quality & Methodology

**Page objective:**  
Show transparently what limitations the analysis has and how they are controlled.

### Main Elements

- List of missing factors: tyres, pit stops, weather, DRS, Safety Car / VSC
- Number of laps before and after cleaning
- Share of excluded laps by team and race
- Table of cleaning rules:
  - individual outlier vs driver's rolling median;
  - field-wide spike vs whole-field median;
  - first-lap exclusion as an optional setting;
  - exclusion of laps with extreme `lap_time_ms` values.
- Comparison of key KPIs before and after cleaning

### Main Question on the Page

**How reliable is the conclusion after accounting for possible distortions in lap-time data?**

---

## 8. Example Conclusion

### If the hypothesis is confirmed

**Conclusion:**  
The analysis confirms that McLaren has an advantage in observed race-pace stability. In Miami and on comparable circuits, the team shows a smaller pace drop-off between the first and final parts of the race than Ferrari, Mercedes, and Red Bull. McLaren's particular strength appears in the second half of the race: the team shows fewer sharp lap-time losses and more often reduces the gap to competitors closer to the finish.

**Important limitation:**  
This conclusion does not prove that McLaren manages tyres better or has a superior pit-stop strategy, because those variables are not available in the data model. The correct interpretation is that McLaren appears more stable in the cleaned lap-time data.

**Practical interpretation for the team:**  
McLaren can build its Miami race approach not only around qualifying position, but also around strong race pace. If the team maintains stable pace after the middle of the race, it can attack competitors in the second half or defend position more effectively over a long stint.

---

### If the hypothesis is rejected

**Conclusion:**  
The analysis does not confirm McLaren's advantage in observed race-pace stability. In Miami and on comparable circuits, McLaren does not show a smaller pace drop-off than Ferrari, Mercedes, and Red Bull. Moreover, in the second half of the race, the team either loses relative pace or does not gain a meaningful advantage over its rivals.

**Important limitation:**  
This result does not mean McLaren definitely lacks advantages in tyres, setup, or strategy. It means only that the available lap-time data, without tyre, pit-stop, weather, DRS, and Safety Car information, does not support the stated hypothesis.

**Practical interpretation for the team:**  
McLaren should not rely only on race-pace stability as the key competitive advantage. For a strong result in Miami, greater emphasis should be placed on qualifying, starting position, track-position defence, and minimising losses on individual laps.

---

## 9. Example Story for a Video

### Working Title

**“Can McLaren win Miami through pace stability rather than single-lap speed?”**

---

### 5-Minute Storyline

**0:00–0:30 — Context**

“Before the Miami race, McLaren needs to understand where its real advantage may come from. Being fast over one lap is not enough: in the race, success often belongs not to the team with the best single lap time, but to the team that can sustain pace over the full distance.”

---

**0:30–1:00 — Data limitation**

“In this data model, we have detailed lap times, positions, teams, drivers, and results, but we do not have tyre, pit-stop, weather, DRS, or Safety Car data. Therefore, we will not make claims about pure tyre degradation or strategy quality. We are analysing observed race pace from lap-time data and separately filtering potentially anomalous laps.”

---

**1:00–1:30 — Hypothesis**

“My hypothesis is that McLaren's advantage over Ferrari, Mercedes, and Red Bull is in observed race-pace stability. The team does not need to be faster on every lap if its pace deteriorates less from the beginning to the end of the race.”

---

**1:30–2:10 — Executive view**

“On the first dashboard page, we compare teams using two key metrics: Observed Pace Drift and Lap Time Variability. If McLaren is lower than its rivals on both metrics, it means the team is more stable over the race distance in the cleaned lap-time data.”

---

**2:10–3:00 — Lap-by-lap evolution**

“Now we move from averages to race evolution by lap. The important line is Relative Pace Delta. If McLaren's line improves in the second half of the race, the team is not only maintaining pace — it is becoming stronger relative to its competitors.”

---

**3:00–3:50 — Race phases**

“Let's split the race into three phases: early, middle, and late. The most important part is the final third of the distance. This is where pace stability becomes especially valuable. If McLaren loses less time in this phase, it could become a strategic advantage in Miami.”

---

**3:50–4:30 — Miami vs similar circuits**

“Because Miami has a short history, we expand the analysis to similar circuits. This helps us understand whether McLaren's stability is a one-race coincidence or a repeatable pattern on tracks with similar characteristics.”

---

**4:30–4:50 — Reliability check**

“It is also important to compare the result on raw laps and cleaned laps. If McLaren's advantage remains after removing potential pit-stop laps, Safety Car laps, and other anomalies, the conclusion becomes more reliable.”

---

**4:50–5:00 — Final takeaway**

“The final question for the team is simple: can McLaren build its Miami race around stable race pace? If the hypothesis is confirmed, the team can focus on a strong second half of the race. If not, qualifying, starting position, and track-position defence become the key priorities.”

---

## Final Project Formulation

**Dashboard objective:**  
Assess whether McLaren's observed race-pace stability is a potential competitive advantage over Ferrari, Mercedes, and Red Bull at the Miami Grand Prix.

**Fundamental question:**  
Can McLaren aim for a strong Miami result through more stable long-run race pace?

**Hypothesis:**  
McLaren shows lower observed pace drop-off and lower lap-time variability in the cleaned lap-time data than its main competitors, which could make the team especially competitive in the second half of the Miami Grand Prix.

**Key limitation:**  
Because the data model does not include tyre, pit-stop, weather, DRS, or Safety Car information, the analysis must be interpreted as an assessment of observed pace stability, not as causal proof of tyre degradation, strategy effectiveness, or external-condition effects.
