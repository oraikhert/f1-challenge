# 5-Minute Presentation Script: Late Pace Conversion Power BI Report

This script is written to be read aloud. It uses `Season = 2025` as the main example. If another filter context is selected during the presentation, keep the same logic and read the values currently shown on the report.

## Presentation Storyline

The cleanest story is:

```text
Start with the overall verdict, then show the evidence behind it, then show how the report can be used for practical analysis.
```

Use all three report pages in this order:

1. `Page 1: Executive Verdict`
2. `Page 2: Evidence & Relationship`
3. `Page 3: Strategic Application`

Recommended timing:

| Time | Section | Goal |
|---:|---|---|
| 0:00-0:45 | Hypothesis and terminology | Explain what is being tested |
| 0:45-1:45 | Page 1 | Give the headline answer |
| 1:45-3:00 | Page 2 | Explain the evidence and the relationship |
| 3:00-4:30 | Page 3 | Show practical use cases and segments |
| 4:30-5:00 | Final conclusion | Summarize the result and limitations |

## 1. Opening: Hypothesis and Key Terms

### Presenter Action

Open `Page 1: Executive Verdict` and select `Season = 2025`.

### Script

```text
The purpose of this report is to test whether late-race pace is connected with a driver's ability to gain positions by the end of the race.

The hypothesis is: drivers who improve their relative pace in the late phase of the race are more likely to gain positions by the finish.

The unit of analysis is one driver in one race. So each observation represents a specific driver's race result in a specific Grand Prix.
```

```text
There are three important terms.

First, Position Gain equals Start Position minus Finish Position. If the value is positive, the driver gained positions. If it is zero, the driver held position. If it is negative, the driver lost positions.

Second, Relative Pace % measures a driver's pace relative to the median pace of the field in the same race phase. A negative value means the driver was faster than the median. A positive value means the driver was slower.

Third, Late Pace Gain compares the late phase of the race with the middle phase. A positive Late Pace Gain means the driver improved in the late phase relative to the field.
```

```text
The main comparison is between two groups: Late Pace Improved and Late Pace Did Not Improve.

The hypothesis is supported when the Conversion Rate for Late Pace Improved is higher than the Conversion Rate for Late Pace Did Not Improve.

Here, Conversion Rate means the share of observations where the driver gained positions.
```

```text
One important note: this report does not prove causality. It tests whether there is a useful relationship between late pace and position gain.
```

## 2. Page 1: Executive Verdict

### Presenter Action

Stay on `Page 1` with `Season = 2025` selected.

### Script

```text
Page 1 gives the headline answer.

For the 2025 season, we have 417 observations.

Among drivers who improved their late pace, 53.63% gained positions.

Among drivers who did not improve their late pace, the conversion rate is lower, at 43.70%.

So the Conversion Gap is 9.93 percentage points.
```

```text
The median position gain tells the same story.

For Late Pace Improvers, the median gain is plus 1 position.

For Non-Improvers, the median gain is 0.

So both headline metrics point in the same direction: late pace improvers gained positions more often, and their median outcome was better.
```

```text
The stacked chart below shows the same comparison visually.

The blue segment is the share of drivers who gained positions. That share is larger for the Late Pace Improved group.

The orange segment is the share of drivers who lost positions. That share is larger for the Late Pace Did Not Improve group.

So the overall verdict for 2025 is: the hypothesis is supported in this selected context.
```

### Transition

```text
Page 1 gives us the answer, but it does not show whether the relationship is clean or noisy.

For that, I will move to Page 2.
```

## 3. Page 2: Evidence and Relationship

### Presenter Action

Open `Page 2: Evidence & Relationship`. Keep `Season = 2025` selected.

### Script

```text
Page 2 shows the shape of the relationship.

On the left, the scatter plot shows individual observations. Each point is one driver in one race.

The X-axis is Late Pace Gain. Points to the right of zero are drivers who improved late pace. Points to the left of zero are drivers whose late pace declined.

The Y-axis is Position Gain. Points above zero gained positions. Points below zero lost positions.
```

```text
If the hypothesis worked perfectly, we would expect most points on the right side to be above zero.

But the chart shows a more realistic pattern. The relationship is noisy. There are many points around zero, and there are also counterexamples.

That means Late Pace Gain is not a guarantee of gaining positions. It is a performance signal that needs race context.
```

```text
The chart on the right groups the observations into Late Pace Gain buckets.

The buckets range from Large pace decline to Large pace gain.

This makes the pattern easier to read. For example, in the 2025 season, the Large pace gain bucket has a median Position Gain of 1, and the evidence table shows that 69.70% of those observations gained positions.
```

```text
The evidence table is important because it also shows the sample size.

For example, Large pace gain has 33 observations, while Small pace decline has 128 observations.

So we should not read only the height of the bars. We should always check both the median outcome and the number of observations behind it.
```

```text
The main takeaway from Page 2 is that the relationship exists, but it is not perfectly linear.

Large positive late pace gain is usually a stronger signal, but position gain also depends on starting position, traffic, strategy, track characteristics, pit stops, and race events.
```

### Transition

```text
So far, we know that the hypothesis is supported overall, and we know that the relationship is noisy.

The next question is practical: where is this signal most useful?

That is what Page 3 is for.
```

## 4. Page 3: Strategic Application

### Presenter Action

Open `Page 3: Strategic Application`. Keep `Season = 2025` selected.

### Script

```text
Page 3 turns the analysis into a practical tool.

The bar chart on the left compares the share of gained positions by starting position group and late pace group.

This is important because starting position changes the opportunity to gain places.

A driver starting near the front has fewer positions available to gain. A driver starting near the back has more upside, but that does not always mean the late pace signal is the main reason for the gain.
```

```text
The most useful area is often the midfield.

For example, in the 2025 Upper Midfield group, drivers with Late Pace Improved converted at 51.16%, while drivers without late pace improvement converted at 30.51%.

That is a gap of 20.65 percentage points.

The median outcome is also much better: plus 1 position for improvers versus minus 1 for non-improvers.
```

```text
This is a good example of a segment where the signal is practically useful.

In the midfield, there are usually enough cars nearby to make position gain possible, but the driver still needs pace to convert that opportunity.
```

```text
The Conversion Matrix shows the same idea as counts.

It separates observations into four scenarios: late pace improved or did not improve, and gained positions or did not gain positions.

The most important positive group is Late Pace Improved and Gained Positions.

The most interesting diagnostic group is Late Pace Improved but Did Not Gain Positions. These are cases where the performance signal existed, but it did not turn into a position gain.
```

```text
The Constructors Rating adds another practical angle.

It shows which teams converted their race context into position gain more effectively.

This should not be read only as pure car pace. It can also reflect strategy, starting position, race execution, and the type of races where the team was competitive.
```

```text
Finally, the Unconverted Late Pace Cases table is where we can investigate specific examples.

These are drivers who had Late Pace Gain but did not gain positions.

That table is useful because it turns the report from a summary dashboard into an analysis workflow. We can open a specific race, look at the driver, the start and finish positions, the late pace gain, and ask why the pace did not convert.
```

### Optional Short Drill-Down

Use this only if there is time.

```text
As a quick drill-down, I would use the Upper Midfield group in 2025.

This segment has 102 observations, so it is not too small.

The hypothesis is clearly supported here: Late Pace Improvers convert at 51.16%, while Non-Improvers convert at 30.51%.

The Median Gain Gap is 2 positions.

This makes the Upper Midfield a strong example of where late pace improvement is not just statistically interesting, but practically meaningful.
```

## 5. Final Conclusion

### Script

```text
The final conclusion is that the hypothesis is supported for the selected 2025 context.

Drivers with Late Pace Gain gained positions more often than drivers without late pace improvement.

The overall Conversion Rate is 53.63% for improvers versus 43.70% for non-improvers, and the median gain is also better: plus 1 position versus 0.
```

```text
However, Late Pace Gain is not a guarantee of overtaking.

It is a useful performance signal, but conversion into positions depends on context: starting position, traffic, strategy, track layout, pit stop timing, safety cars, and how many laps are left.
```

```text
The practical value of the report is that it helps identify where the signal works best and where it fails to convert.

Page 1 answers whether the hypothesis is supported.

Page 2 explains the evidence and the shape of the relationship.

Page 3 shows where to apply the insight and which specific cases need further investigation.
```

```text
In one sentence: Late Pace Gain can be used as a practical signal of attack potential, but conversion into positions is context-dependent.
```

## Backup Q&A

### What does "higher Conversion Rate" mean?

```text
It means that a larger share of drivers in that group gained positions.

We compare Late Pace Improved against Late Pace Did Not Improve.

So the hypothesis is supported when Conversion Rate for Late Pace Improved is higher than Conversion Rate for Late Pace Did Not Improve.
```

### Does positive Late Pace Gain always mean the driver was fast?

```text
It means the driver improved relative to the field from the middle phase to the late phase.

It does not automatically mean the driver was the fastest overall.

It is a relative improvement signal, not a full race pace ranking.
```

### Why can a driver improve late pace but still lose positions?

```text
Because position gain depends on more than pace.

A driver may improve late pace after already losing positions earlier in the race. They may also be stuck in traffic, lack overtaking opportunity, face a difficult track position, or run out of laps.

That is why the report includes Unconverted Late Pace Cases.
```

### Why is the midfield important?

```text
The midfield often has the best balance between opportunity and competition.

There are usually cars close enough to attack, but the driver still needs enough pace advantage to convert.

That is why the Upper Midfield segment is a useful drill-down example.
```
