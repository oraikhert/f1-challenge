# Пошаговая инструкция для новичка: Power BI отчет Late Pace Conversion

Эта инструкция помогает собрать Power BI-репорт по заданию из `task_statement/f1_powerbi_task_statement_en.md`.

Цель отчета: проверить гипотезу, что пилоты, которые улучшают относительный темп в поздней фазе гонки, чаще отыгрывают позиции к финишу.

## 1. Что должно получиться

Итоговый отчет должен отвечать на один главный вопрос:

**Есть ли у пилотов с улучшением позднего темпа более высокая вероятность отыграть позиции к финишу?**

Рекомендуемая структура отчета:

1. `Executive Verdict` - общий вывод по гипотезе.
2. `Evidence & Relationship` - связь между улучшением темпа и изменением позиции.
3. `Strategic Application` - где улучшение позднего темпа реально конвертируется в позиции.

Единица анализа: **один пилот в одной гонке**.

## 2. Какие файлы нужны

Для отчета нужны эти CSV-файлы из папки `dataset`:

- `results.csv` - стартовая позиция, финишная позиция, конструктор, статус.
- `lap_times.csv` - времена кругов по пилоту и гонке.
- `races.csv` - сезон, раунд, дата и название Гран-при.
- `drivers.csv` - имена пилотов.
- `constructors.csv` - названия команд / конструкторов.

Файлы `driver_standings.csv` и `cons_standings.csv` для базовой версии отчета не нужны.

## 3. Создание Power BI-файла

1. Открой Power BI Desktop.
2. Создай новый пустой отчет.
3. Нажми `Home` -> `Get data` -> `Text/CSV`.
4. По очереди загрузи пять файлов:
   - `dataset/results.csv`;
   - `dataset/lap_times.csv`;
   - `dataset/races.csv`;
   - `dataset/drivers.csv`;
   - `dataset/constructors.csv`.
5. Для каждого файла выбирай `Transform Data`, а не сразу `Load`.
6. В Power Query переименуй запросы строго так:
   - `results`;
   - `lap_times`;
   - `races`;
   - `drivers`;
   - `constructors`.

Важно: названия запросов должны совпадать с этим списком, потому что готовый код ниже ссылается именно на них.

Если Power Query автоматически добавил шаг `Changed Type` в сырых запросах и где-то появились ошибки из-за значений `\N`, удали этот шаг в панели `Applied Steps`. Итоговый запрос `DriverRaceAnalysis` сам задает нужные типы данных для используемых колонок.

## 4. Создание итоговой аналитической таблицы

Итоговая таблица будет называться `DriverRaceAnalysis`. В ней одна строка означает одного пилота в одной гонке.

### 4.1. Добавь новый пустой запрос

1. В Power Query нажми `Home` -> `New Source` -> `Blank Query`.
2. В панели слева переименуй новый запрос в `DriverRaceAnalysis`.
3. Нажми `Home` -> `Advanced Editor`.
4. Удали весь текст в редакторе.
5. Вставь код ниже.
6. Нажми `Done`.

```powerquery
let
    Results0 = results,
    LapTimes0 = lap_times,
    Races0 = races,
    Drivers0 = drivers,
    Constructors0 = constructors,

    Results = Table.TransformColumnTypes(
        Results0,
        {
            {"race_ID", Int64.Type},
            {"driver_ID", Int64.Type},
            {"constructor_ID", Int64.Type},
            {"starting_position", Int64.Type},
            {"race_position", Int64.Type}
        }
    ),

    LapTimes = Table.TransformColumnTypes(
        LapTimes0,
        {
            {"race_ID", Int64.Type},
            {"driver_ID", Int64.Type},
            {"lap_num", Int64.Type},
            {"position", Int64.Type},
            {"lap_time_ms", Int64.Type}
        }
    ),

    RacesTyped = Table.TransformColumnTypes(
        Races0,
        {
            {"race_ID", Int64.Type},
            {"year", Int64.Type},
            {"round", Int64.Type},
            {"circuit_ID", Int64.Type},
            {"circuit_location", type text},
            {"circuit_country", type text},
            {"circuit_name", type text},
            {"race_date", type text}
        }
    ),

    Races = Table.TransformColumns(
        RacesTyped,
        {
            {
                "race_date",
                each try Date.FromText(_, [Format = "dd/MM/yyyy", Culture = "en-GB"]) otherwise null,
                type date
            }
        }
    ),

    Drivers = Table.TransformColumnTypes(
        Drivers0,
        {
            {"driver_ID", Int64.Type},
            {"driver_ref", type text},
            {"driver_code", type text},
            {"driver_forename", type text},
            {"driver_surname", type text},
            {"driver_nationality", type text}
        }
    ),

    Constructors = Table.TransformColumnTypes(
        Constructors0,
        {
            {"constructor_ID", Int64.Type},
            {"constructor_ref", type text},
            {"constructor_name", type text},
            {"constructor_nationality", type text}
        }
    ),

    RaceLapCounts = Table.Group(
        LapTimes,
        {"race_ID"},
        {{"Race Lap Count", each List.Max([lap_num]), Int64.Type}}
    ),

    LapWithRaceLapCount = Table.NestedJoin(
        LapTimes,
        {"race_ID"},
        RaceLapCounts,
        {"race_ID"},
        "RaceLaps",
        JoinKind.Inner
    ),

    LapExpanded = Table.ExpandTableColumn(
        LapWithRaceLapCount,
        "RaceLaps",
        {"Race Lap Count"},
        {"Race Lap Count"}
    ),

    AddLapProgress = Table.AddColumn(
        LapExpanded,
        "Lap Progress",
        each Number.From([lap_num]) / Number.From([Race Lap Count]),
        Percentage.Type
    ),

    AddRacePhase = Table.AddColumn(
        AddLapProgress,
        "Race Phase",
        each
            if [Lap Progress] > 0.35 and [Lap Progress] <= 0.65 then "Middle"
            else if [Lap Progress] > 0.70 then "Late"
            else "Other",
        type text
    ),

    PhaseLaps = Table.SelectRows(
        AddRacePhase,
        each
            ([Race Phase] = "Middle" or [Race Phase] = "Late")
            and [lap_time_ms] <> null
            and [lap_time_ms] > 0
    ),

    DriverPhasePace = Table.Group(
        PhaseLaps,
        {"race_ID", "driver_ID", "Race Phase"},
        {
            {"Driver Median Lap Time MS", each List.Median([lap_time_ms]), type number},
            {"Phase Lap Count", each Table.RowCount(_), Int64.Type}
        }
    ),

    DriverPhasePaceFiltered = Table.SelectRows(
        DriverPhasePace,
        each [Phase Lap Count] >= 3
    ),

    FieldPhasePace = Table.Group(
        DriverPhasePaceFiltered,
        {"race_ID", "Race Phase"},
        {{"Field Median Lap Time MS", each List.Median([Driver Median Lap Time MS]), type number}}
    ),

    DriverWithFieldPace = Table.NestedJoin(
        DriverPhasePaceFiltered,
        {"race_ID", "Race Phase"},
        FieldPhasePace,
        {"race_ID", "Race Phase"},
        "FieldPace",
        JoinKind.LeftOuter
    ),

    ExpandedFieldPace = Table.ExpandTableColumn(
        DriverWithFieldPace,
        "FieldPace",
        {"Field Median Lap Time MS"},
        {"Field Median Lap Time MS"}
    ),

    AddRelativePace = Table.AddColumn(
        ExpandedFieldPace,
        "Relative Pace %",
        each ([Driver Median Lap Time MS] / [Field Median Lap Time MS]) - 1,
        Percentage.Type
    ),

    PaceForPivot = Table.SelectColumns(
        AddRelativePace,
        {"race_ID", "driver_ID", "Race Phase", "Relative Pace %"}
    ),

    PacePivot = Table.Pivot(
        PaceForPivot,
        List.Distinct(PaceForPivot[Race Phase]),
        "Race Phase",
        "Relative Pace %",
        List.Average
    ),

    PaceRenamed = Table.RenameColumns(
        PacePivot,
        {
            {"Middle", "Middle Relative Pace %"},
            {"Late", "Late Relative Pace %"}
        },
        MissingField.Ignore
    ),

    PaceFiltered = Table.SelectRows(
        PaceRenamed,
        each [#"Middle Relative Pace %"] <> null and [#"Late Relative Pace %"] <> null
    ),

    AddLateImprovement = Table.AddColumn(
        PaceFiltered,
        "Late vs Middle Pace Improvement",
        each [#"Middle Relative Pace %"] - [#"Late Relative Pace %"],
        Percentage.Type
    ),

    ResultsFiltered = Table.SelectRows(
        Results,
        each
            [starting_position] <> null
            and [starting_position] > 0
            and [race_position] <> null
            and [race_position] > 0
    ),

    MergeResults = Table.NestedJoin(
        AddLateImprovement,
        {"race_ID", "driver_ID"},
        ResultsFiltered,
        {"race_ID", "driver_ID"},
        "Results",
        JoinKind.Inner
    ),

    ExpandResults = Table.ExpandTableColumn(
        MergeResults,
        "Results",
        {"constructor_ID", "starting_position", "race_position", "status"},
        {"constructor_ID", "Start Position", "Finish Position", "Status"}
    ),

    AddPositionGain = Table.AddColumn(
        ExpandResults,
        "Position Gain",
        each [Start Position] - [Finish Position],
        Int64.Type
    ),

    MergeRaces = Table.NestedJoin(
        AddPositionGain,
        {"race_ID"},
        Races,
        {"race_ID"},
        "Races",
        JoinKind.LeftOuter
    ),

    ExpandRaces = Table.ExpandTableColumn(
        MergeRaces,
        "Races",
        {"year", "round", "circuit_name", "circuit_country", "race_date"},
        {"Season", "Round", "Grand Prix", "Country", "Race Date"}
    ),

    MergeDrivers = Table.NestedJoin(
        ExpandRaces,
        {"driver_ID"},
        Drivers,
        {"driver_ID"},
        "Drivers",
        JoinKind.LeftOuter
    ),

    ExpandDrivers = Table.ExpandTableColumn(
        MergeDrivers,
        "Drivers",
        {"driver_code", "driver_forename", "driver_surname", "driver_nationality"},
        {"Driver Code", "Driver Forename", "Driver Surname", "Driver Nationality"}
    ),

    AddDriverName = Table.AddColumn(
        ExpandDrivers,
        "Driver",
        each Text.Trim(Text.Combine({[Driver Forename], [Driver Surname]}, " ")),
        type text
    ),

    MergeConstructors = Table.NestedJoin(
        AddDriverName,
        {"constructor_ID"},
        Constructors,
        {"constructor_ID"},
        "Constructors",
        JoinKind.LeftOuter
    ),

    ExpandConstructors = Table.ExpandTableColumn(
        MergeConstructors,
        "Constructors",
        {"constructor_name", "constructor_nationality"},
        {"Constructor", "Constructor Nationality"}
    ),

    AddLatePaceGroup = Table.AddColumn(
        ExpandConstructors,
        "Late Pace Group",
        each if [#"Late vs Middle Pace Improvement"] > 0 then "Late Pace Improved" else "Late Pace Did Not Improve",
        type text
    ),

    AddPositionOutcome = Table.AddColumn(
        AddLatePaceGroup,
        "Position Outcome",
        each
            if [Position Gain] > 0 then "Gained Positions"
            else if [Position Gain] = 0 then "Held Position"
            else "Lost Positions",
        type text
    ),

    AddPositionGainFlag = Table.AddColumn(
        AddPositionOutcome,
        "Position Gain Flag",
        each if [Position Gain] > 0 then "Gained Positions" else "Did Not Gain Positions",
        type text
    ),

    AddStartingPositionGroup = Table.AddColumn(
        AddPositionGainFlag,
        "Starting Position Group",
        each
            if [Start Position] <= 5 then "Front: P1-P5"
            else if [Start Position] <= 10 then "Upper Midfield: P6-P10"
            else if [Start Position] <= 15 then "Lower Midfield: P11-P15"
            else "Back: P16+",
        type text
    ),

    AddPaceImprovementBucket = Table.AddColumn(
        AddStartingPositionGroup,
        "Pace Improvement Bucket",
        each
            if [#"Late vs Middle Pace Improvement"] < -0.01 then "< -1.0 pp"
            else if [#"Late vs Middle Pace Improvement"] < -0.005 then "-1.0 to -0.5 pp"
            else if [#"Late vs Middle Pace Improvement"] < 0 then "-0.5 to 0 pp"
            else if [#"Late vs Middle Pace Improvement"] < 0.005 then "0 to +0.5 pp"
            else if [#"Late vs Middle Pace Improvement"] < 0.01 then "+0.5 to +1.0 pp"
            else "> +1.0 pp",
        type text
    ),

    AddPaceImprovementBucketSort = Table.AddColumn(
        AddPaceImprovementBucket,
        "Pace Improvement Bucket Sort",
        each
            if [#"Late vs Middle Pace Improvement"] < -0.01 then 1
            else if [#"Late vs Middle Pace Improvement"] < -0.005 then 2
            else if [#"Late vs Middle Pace Improvement"] < 0 then 3
            else if [#"Late vs Middle Pace Improvement"] < 0.005 then 4
            else if [#"Late vs Middle Pace Improvement"] < 0.01 then 5
            else 6,
        Int64.Type
    ),

    AddConversionQuadrant = Table.AddColumn(
        AddPaceImprovementBucketSort,
        "Conversion Quadrant",
        each
            if [#"Late vs Middle Pace Improvement"] > 0 and [Position Gain] > 0 then "Successful Conversion"
            else if [#"Late vs Middle Pace Improvement"] > 0 and [Position Gain] <= 0 then "Unconverted Late Pace"
            else if [#"Late vs Middle Pace Improvement"] <= 0 and [Position Gain] > 0 then "External / Non-Pace Gain"
            else "Expected Weakness",
        type text
    ),

    AddObservationID = Table.AddColumn(
        AddConversionQuadrant,
        "Observation ID",
        each Text.From([race_ID]) & "-" & Text.From([driver_ID]),
        type text
    ),

    ReorderedColumns = Table.ReorderColumns(
        AddObservationID,
        {
            "Observation ID",
            "race_ID",
            "driver_ID",
            "constructor_ID",
            "Season",
            "Round",
            "Race Date",
            "Grand Prix",
            "Country",
            "Driver",
            "Driver Code",
            "Constructor",
            "Start Position",
            "Finish Position",
            "Position Gain",
            "Middle Relative Pace %",
            "Late Relative Pace %",
            "Late vs Middle Pace Improvement",
            "Late Pace Group",
            "Position Outcome",
            "Position Gain Flag",
            "Starting Position Group",
            "Pace Improvement Bucket",
            "Pace Improvement Bucket Sort",
            "Conversion Quadrant",
            "Status",
            "Driver Nationality",
            "Constructor Nationality"
        },
        MissingField.Ignore
    )
in
    ReorderedColumns
```

### 4.2. Что делает этот код

Код выполняет все основные расчеты:

- берет только гонки, где есть времена кругов;
- делит дистанцию гонки на фазы;
- считает средний уровень темпа пилота через медианное время круга;
- сравнивает темп пилота с медианой пелотона в той же гонке и фазе;
- рассчитывает `Middle Relative Pace %`;
- рассчитывает `Late Relative Pace %`;
- рассчитывает `Late vs Middle Pace Improvement`;
- добавляет стартовую позицию, финишную позицию, пилота, команду и гонку;
- рассчитывает `Position Gain = Start Position - Finish Position`;
- создает группы для визуализаций.

В этой инструкции используются такие фазы гонки:

- `Middle`: от 35% до 65% дистанции;
- `Late`: после 70% дистанции.

Это простой и понятный вариант для первой версии отчета. Если нужно, границы фаз можно поменять в строках с `AddRacePhase`.

## 5. Настройка модели данных

После создания `DriverRaceAnalysis`:

1. Нажми `Close & Apply`.
2. Перейди во вкладку `Model view`.
3. Для первой версии отчета можно оставить только таблицу `DriverRaceAnalysis` в визуализациях.
4. Сырые таблицы (`results`, `lap_times`, `races`, `drivers`, `constructors`) лучше скрыть:
   - правый клик по таблице;
   - `Hide in report view`.

Это снизит риск случайно использовать неправильное поле в графике.

## 6. Настройка форматов полей

В `Data view` выбери таблицу `DriverRaceAnalysis` и настрой поля:

- `Middle Relative Pace %` -> формат `Percentage`, 2 знака после запятой.
- `Late Relative Pace %` -> формат `Percentage`, 2 знака после запятой.
- `Late vs Middle Pace Improvement` -> формат `Percentage`, 2 знака после запятой.
- `Position Gain` -> формат `Whole number`.
- `Start Position` -> формат `Whole number`.
- `Finish Position` -> формат `Whole number`.
- `Race Date` -> формат `Date`.

Для сортировки bucket-поля:

1. Выбери колонку `Pace Improvement Bucket`.
2. Нажми `Column tools` -> `Sort by column`.
3. Выбери `Pace Improvement Bucket Sort`.

## 7. Создание DAX-мер

В Power BI перейди в `Report view`.

1. Правый клик по таблице `DriverRaceAnalysis`.
2. Нажми `New measure`.
3. Создай меры ниже по одной.

### 7.1. Базовые меры

```dax
Observations =
COUNTROWS('DriverRaceAnalysis')
```

```dax
Gained Positions Count =
CALCULATE(
    [Observations],
    'DriverRaceAnalysis'[Position Gain] > 0
)
```

```dax
% Gained Positions =
DIVIDE(
    [Gained Positions Count],
    [Observations]
)
```

```dax
Median Position Gain =
MEDIAN('DriverRaceAnalysis'[Position Gain])
```

```dax
Median Late Pace Improvement =
MEDIAN('DriverRaceAnalysis'[Late vs Middle Pace Improvement])
```

### 7.2. KPI для проверки гипотезы

```dax
Conversion Rate - Improvers =
DIVIDE(
    CALCULATE(
        [Observations],
        'DriverRaceAnalysis'[Late Pace Group] = "Late Pace Improved",
        'DriverRaceAnalysis'[Position Gain] > 0
    ),
    CALCULATE(
        [Observations],
        'DriverRaceAnalysis'[Late Pace Group] = "Late Pace Improved"
    )
)
```

```dax
Conversion Rate - Non-Improvers =
DIVIDE(
    CALCULATE(
        [Observations],
        'DriverRaceAnalysis'[Late Pace Group] = "Late Pace Did Not Improve",
        'DriverRaceAnalysis'[Position Gain] > 0
    ),
    CALCULATE(
        [Observations],
        'DriverRaceAnalysis'[Late Pace Group] = "Late Pace Did Not Improve"
    )
)
```

```dax
Median Position Gain - Improvers =
CALCULATE(
    [Median Position Gain],
    'DriverRaceAnalysis'[Late Pace Group] = "Late Pace Improved"
)
```

```dax
Median Position Gain - Non-Improvers =
CALCULATE(
    [Median Position Gain],
    'DriverRaceAnalysis'[Late Pace Group] = "Late Pace Did Not Improve"
)
```

```dax
Position Gain Difference =
[Median Position Gain - Improvers] - [Median Position Gain - Non-Improvers]
```

### 7.3. Дополнительная мера корреляции

Эта мера считает ранговую корреляцию между улучшением позднего темпа и изменением позиции. Она нужна как дополнительное доказательство, но не как главный KPI.

```dax
Spearman Correlation =
VAR BaseRows =
    FILTER(
        ALLSELECTED('DriverRaceAnalysis'),
        NOT ISBLANK('DriverRaceAnalysis'[Late vs Middle Pace Improvement])
            && NOT ISBLANK('DriverRaceAnalysis'[Position Gain])
    )
VAR RankedRows =
    ADDCOLUMNS(
        BaseRows,
        "__RankPace",
            RANKX(
                BaseRows,
                'DriverRaceAnalysis'[Late vs Middle Pace Improvement],
                ,
                ASC,
                Dense
            ),
        "__RankGain",
            RANKX(
                BaseRows,
                'DriverRaceAnalysis'[Position Gain],
                ,
                ASC,
                Dense
            )
    )
VAR AvgRankPace =
    AVERAGEX(RankedRows, [__RankPace])
VAR AvgRankGain =
    AVERAGEX(RankedRows, [__RankGain])
VAR Numerator =
    SUMX(
        RankedRows,
        ([__RankPace] - AvgRankPace) * ([__RankGain] - AvgRankGain)
    )
VAR Denominator =
    SQRT(
        SUMX(RankedRows, POWER([__RankPace] - AvgRankPace, 2))
            * SUMX(RankedRows, POWER([__RankGain] - AvgRankGain, 2))
    )
RETURN
    DIVIDE(Numerator, Denominator)
```

Если Power BI показывает ошибку на этой мере, временно пропусти ее. Корреляция является дополнительным элементом, а главные выводы строятся на conversion rate и медианном `Position Gain`.

## 8. Общие фильтры отчета

На каждую страницу можно добавить slicer-фильтры:

- `Season`;
- `Constructor`;
- `Driver`;
- `Starting Position Group`;
- `Grand Prix`.

Для первой версии достаточно двух фильтров:

- `Season`;
- `Starting Position Group`.

Так отчет будет проще читать.

## 9. Страница 1: Executive Verdict

Цель страницы: сразу показать, подтверждается ли гипотеза.

### 9.1. Добавь заголовок

Добавь текст:

```text
Executive Verdict: Does Late Pace Convert Into Positions?
```

### 9.2. Добавь KPI-карточки

Создай четыре `Card` visual:

1. `Conversion Rate - Improvers`
2. `Median Position Gain - Improvers`
3. `Median Position Gain - Non-Improvers`
4. `Position Gain Difference`

Настройки:

- для `Conversion Rate - Improvers` используй формат `Percentage`;
- для медианных позиций используй 1 знак после запятой;
- подписи карточек сделай короткими:
  - `Conversion Rate`;
  - `Median Gain: Improvers`;
  - `Median Gain: Non-Improvers`;
  - `Median Gain Gap`.

### 9.3. Добавь график долей исходов

Используй `100% stacked column chart`.

Поля:

- X-axis: `Late Pace Group`;
- Legend: `Position Outcome`;
- Values: `Observations`.

Этот график отвечает на вопрос: у какой группы больше доля `Gained Positions`.

### 9.4. Добавь текстовый вывод

Добавь текстовый блок с выводом. Используй один из вариантов:

```text
Hypothesis supported: late pace improvers show higher conversion rate and higher median position gain.
```

```text
Hypothesis partially supported: the overall effect exists, but it depends on starting position group or constructor.
```

```text
Hypothesis not supported: late pace improvers do not gain positions more often than non-improvers.
```

Выбирай формулировку после просмотра KPI.

## 10. Страница 2: Evidence & Relationship

Цель страницы: показать форму связи между улучшением темпа и изменением позиции.

### 10.1. Scatter plot

Добавь `Scatter chart`.

Поля:

- X-axis: `Late vs Middle Pace Improvement`;
- Y-axis: `Position Gain`;
- Legend: `Position Outcome`;
- Details: `Observation ID`;
- Tooltips:
  - `Season`;
  - `Grand Prix`;
  - `Driver`;
  - `Constructor`;
  - `Start Position`;
  - `Finish Position`;
  - `Middle Relative Pace %`;
  - `Late Relative Pace %`.

Настройки:

- X-axis форматируй как процент;
- добавь вертикальную reference line на `0`;
- добавь горизонтальную reference line на `0`;
- точку справа от нуля по X можно читать как улучшение позднего темпа;
- точку выше нуля по Y можно читать как отыгранные позиции.

### 10.2. Bar chart по bucket

Добавь `Clustered column chart`.

Поля:

- X-axis: `Pace Improvement Bucket`;
- Values: `Median Position Gain`.

Проверь, что `Pace Improvement Bucket` отсортирован по `Pace Improvement Bucket Sort`.

### 10.3. Таблица evidence

Добавь `Table` visual.

Поля:

- `Pace Improvement Bucket`;
- `Observations`;
- `Median Position Gain`;
- `% Gained Positions`.

Сортировка:

- сортируй по `Pace Improvement Bucket Sort` по возрастанию.

Главный вопрос этой страницы:

```text
Does stronger late pace improvement usually correspond to better positional outcome?
```

## 11. Страница 3: Strategic Application

Цель страницы: показать, где улучшение позднего темпа полезнее всего для команды.

### 11.1. Conversion Rate by Starting Position Group

Добавь `Clustered column chart`.

Поля:

- X-axis: `Starting Position Group`;
- Legend: `Late Pace Group`;
- Values: `% Gained Positions`.

Интерпретация:

- если `Late Pace Improved` выше в конкретной стартовой группе, гипотеза лучше работает именно там;
- если разницы нет, поздний темп в этой группе плохо объясняет изменение позиции.

### 11.2. Рейтинг конструкторов

Добавь `Table` или `Matrix`.

Поля:

- `Constructor`;
- `Observations`;
- `Median Late Pace Improvement`;
- `% Gained Positions`;
- `Median Position Gain`.

Рекомендуемый фильтр:

- оставь только конструкторов с достаточным числом наблюдений, например `Observations >= 20`.

Это нужно, чтобы не делать выводы по слишком маленьким выборкам.

### 11.3. 2x2 conversion matrix

Добавь `Matrix` visual.

Поля:

- Rows: `Late Pace Group`;
- Columns: `Position Gain Flag`;
- Values: `Observations`.

Матрица показывает четыре сценария:

- `Late Pace Improved` + `Gained Positions` = successful conversion;
- `Late Pace Improved` + `Did Not Gain Positions` = unconverted late pace;
- `Late Pace Did Not Improve` + `Gained Positions` = external / non-pace gain;
- `Late Pace Did Not Improve` + `Did Not Gain Positions` = expected weakness.

### 11.4. Таблица Unconverted Late Pace

Добавь `Table` visual.

Поля:

- `Season`;
- `Grand Prix`;
- `Driver`;
- `Constructor`;
- `Start Position`;
- `Finish Position`;
- `Position Gain`;
- `Middle Relative Pace %`;
- `Late Relative Pace %`;
- `Late vs Middle Pace Improvement`;
- `Status`.

Фильтр visual-level:

- `Conversion Quadrant` = `Unconverted Late Pace`.

Сортировка:

- сортируй по `Late vs Middle Pace Improvement` по убыванию.

Эта таблица показывает случаи, где темп улучшился, но позиции не были отыграны. Это важный список для стратегического разбора.

## 12. Как читать ключевые метрики

### Position Gain

```text
Position Gain = Start Position - Finish Position
```

Интерпретация:

- `> 0` - пилот отыграл позиции;
- `= 0` - пилот удержал позицию;
- `< 0` - пилот потерял позиции.

### Relative Pace %

```text
Relative Pace % = Driver Median Lap Time / Field Median Lap Time - 1
```

Интерпретация:

- отрицательное значение - пилот быстрее медианы пелотона;
- положительное значение - пилот медленнее медианы пелотона.

### Late vs Middle Pace Improvement

```text
Late vs Middle Pace Improvement = Middle Relative Pace % - Late Relative Pace %
```

Интерпретация:

- `> 0` - пилот улучшил относительный темп в поздней фазе;
- `= 0` - темп примерно не изменился;
- `< 0` - пилот ухудшил относительный темп.

Знак выбран так, чтобы большее значение означало лучший результат.

## 13. Как сформулировать финальный вывод

Используй такую логику:

1. Сравни `Conversion Rate - Improvers` и `Conversion Rate - Non-Improvers`.
2. Сравни `Median Position Gain - Improvers` и `Median Position Gain - Non-Improvers`.
3. Посмотри scatter plot: есть ли больше точек в правой верхней зоне.
4. Проверь разрезы на странице 3: стартовая группа и конструктор.

Гипотеза поддержана, если:

- у improvers выше conversion rate;
- у improvers выше median position gain;
- связь видна хотя бы в части важных сегментов.

Гипотеза частично поддержана, если:

- общий эффект есть, но он явно зависит от стартовой позиции, команды или сезона.

Гипотеза не поддержана, если:

- improvers не отыгрывают позиции чаще;
- медианный `Position Gain` у improvers не выше.

## 14. Ограничения анализа, которые нужно упомянуть

В финальном комментарии к отчету обязательно укажи:

- отчет показывает связь, но не доказывает причинно-следственную зависимость;
- на изменение позиции влияют пит-стопы, трафик, Safety Car, погода, штрафы, сходы и командная тактика;
- `race_ID` не используется для хронологии, потому что это технический идентификатор;
- период анализа начинается с гонок, где есть lap times, то есть старые сезоны без времен кругов не входят в расчет;
- медиана используется вместо среднего, чтобы снизить влияние очень медленных кругов, пит-стопов и выбросов.

## 15. Финальная проверка перед сдачей

Перед сдачей отчета проверь:

- на странице 1 есть четыре KPI и общий verdict;
- на странице 2 есть scatter plot, bucket chart и evidence table;
- на странице 3 есть стартовые группы, рейтинг конструкторов, 2x2 matrix и таблица `Unconverted Late Pace`;
- проценты отображаются как проценты, а не как десятичные числа;
- `Pace Improvement Bucket` отсортирован в правильном порядке;
- в таблице `DriverRaceAnalysis` одна строка соответствует одному пилоту в одной гонке;
- вывод сформулирован аккуратно: late pace improvement может быть индикатором positional gain, но не единственной причиной.
