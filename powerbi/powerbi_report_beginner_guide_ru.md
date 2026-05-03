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

Модель данных будет построена как star schema:

- `DriverRaceAnalysis` - основная fact-таблица, одна строка = пилот в гонке;
- `drivers` - dimension-таблица пилотов;
- `constructors` - dimension-таблица команд / конструкторов;
- `races` - dimension-таблица гонок;
- `results` и `lap_times` - служебные staging-запросы для расчета fact-таблицы.

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

Если Power Query автоматически добавил шаг `Changed Type` в сырых запросах и где-то появились ошибки из-за значений `\N`, удали этот шаг в панели `Applied Steps`. Ниже ты отдельно задашь нужные типы для dimensions и fact-таблицы.

## 4. Подготовка dimension-таблиц

Перед созданием fact-таблицы подготовь три dimension-таблицы. Это уменьшит дублирование текста в модели и сделает фильтры отчета чище.

### 4.1. Таблица `drivers`

1. В Power Query выбери запрос `drivers`.
2. Оставь только колонки:
   - `driver_ID`;
   - `driver_code`;
   - `driver_forename`;
   - `driver_surname`;
   - `driver_nationality`.
3. Для `driver_ID` установи тип `Whole Number`.
4. Добавь колонку `Driver`:
   - `Add Column` -> `Custom Column`;
   - имя колонки: `Driver`;
   - формула:

```powerquery
Text.Trim([driver_forename] & " " & [driver_surname])
```

5. Переименуй поля:
   - `driver_code` -> `Driver Code`;
   - `driver_forename` -> `Driver Forename`;
   - `driver_surname` -> `Driver Surname`;
   - `driver_nationality` -> `Driver Nationality`.

### 4.2. Таблица `constructors`

1. В Power Query выбери запрос `constructors`.
2. Оставь только колонки:
   - `constructor_ID`;
   - `constructor_name`;
   - `constructor_nationality`.
3. Для `constructor_ID` установи тип `Whole Number`.
4. Переименуй поля:
   - `constructor_name` -> `Constructor`;
   - `constructor_nationality` -> `Constructor Nationality`.

### 4.3. Таблица `races`

1. В Power Query выбери запрос `races`.
2. Оставь только колонки:
   - `race_ID`;
   - `year`;
   - `round`;
   - `circuit_location`;
   - `circuit_country`;
   - `circuit_name`;
   - `race_date`.
3. Для `race_ID`, `year` и `round` установи тип `Whole Number`.
4. Для `race_date` установи тип `Date` через `Change Type` -> `Using Locale`:
   - Data Type: `Date`;
   - Locale: `English (United Kingdom)`.
5. Переименуй поля:
   - `year` -> `Season`;
   - `round` -> `Round`;
   - `circuit_location` -> `Circuit Location`;
   - `circuit_country` -> `Country`;
   - `circuit_name` -> `Grand Prix`;
   - `race_date` -> `Race Date`.
6. Добавь колонку `Season Sort Desc`:
   - `Add Column` -> `Custom Column`;
   - имя колонки: `Season Sort Desc`;
   - формула:

```powerquery
9999 - [Season]
```

7. Для `Season Sort Desc` установи тип `Whole Number`.

Эта колонка нужна только для сортировки slicer `Season` от новых сезонов к старым. При обычной сортировке по возрастанию значения `Season Sort Desc` порядок сезонов будет `2026`, `2025`, `2024` и так далее.

### 4.4. Служебные staging-запросы

Запросы `results` и `lap_times` нужны только для расчета `DriverRaceAnalysis`. Их не нужно показывать в модели отчета.

1. Правый клик по запросу `results`.
2. Сними галочку `Enable Load`.
3. Повтори то же самое для `lap_times`.

После этого `results` и `lap_times` останутся доступными для Power Query, но не будут загружаться как отдельные таблицы в модель Power BI.

## 5. Создание итоговой fact-таблицы

Итоговая таблица будет называться `DriverRaceAnalysis`. В ней одна строка означает одного пилота в одной гонке.

### 5.1. Добавь новый пустой запрос

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

    AddLatePaceGroup = Table.AddColumn(
        AddPositionGain,
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

    AddStartingPositionGroupSort = Table.AddColumn(
        AddStartingPositionGroup,
        "Starting Position Group Sort",
        each
            if [Start Position] <= 5 then 1
            else if [Start Position] <= 10 then 2
            else if [Start Position] <= 15 then 3
            else 4,
        Int64.Type
    ),

    AddPaceImprovementBucket = Table.AddColumn(
        AddStartingPositionGroupSort,
        "Pace Improvement Bucket",
        each
            if [#"Late vs Middle Pace Improvement"] < -0.01 then "Large pace decline"
            else if [#"Late vs Middle Pace Improvement"] < -0.005 then "Medium pace decline"
            else if [#"Late vs Middle Pace Improvement"] < 0 then "Small pace decline"
            else if [#"Late vs Middle Pace Improvement"] < 0.005 then "Small pace gain"
            else if [#"Late vs Middle Pace Improvement"] < 0.01 then "Medium pace gain"
            else "Large pace gain",
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

    AddPaceImprovementRange = Table.AddColumn(
        AddPaceImprovementBucketSort,
        "Pace Improvement Range",
        each
            if [#"Late vs Middle Pace Improvement"] < -0.01 then "< -1.0 pp"
            else if [#"Late vs Middle Pace Improvement"] < -0.005 then "-1.0 to -0.5 pp"
            else if [#"Late vs Middle Pace Improvement"] < 0 then "-0.5 to 0 pp"
            else if [#"Late vs Middle Pace Improvement"] < 0.005 then "0 to +0.5 pp"
            else if [#"Late vs Middle Pace Improvement"] < 0.01 then "+0.5 to +1.0 pp"
            else "> +1.0 pp",
        type text
    ),

    AddConversionQuadrant = Table.AddColumn(
        AddPaceImprovementRange,
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
            "Starting Position Group Sort",
            "Pace Improvement Bucket",
            "Pace Improvement Range",
            "Pace Improvement Bucket Sort",
            "Conversion Quadrant",
            "Status"
        },
        MissingField.Ignore
    )
in
    ReorderedColumns
```

### 5.2. Что делает этот код

Код выполняет все основные расчеты:

- берет только гонки, где есть времена кругов;
- делит дистанцию гонки на фазы;
- считает средний уровень темпа пилота через медианное время круга;
- сравнивает темп пилота с медианой пелотона в той же гонке и фазе;
- рассчитывает `Middle Relative Pace %`;
- рассчитывает `Late Relative Pace %`;
- рассчитывает `Late vs Middle Pace Improvement`;
- добавляет стартовую позицию, финишную позицию и `constructor_ID` из `results`;
- рассчитывает `Position Gain = Start Position - Finish Position`;
- оставляет `race_ID`, `driver_ID` и `constructor_ID` как ключи для связей с dimensions;
- создает группы для визуализаций.

В этой инструкции используются такие фазы гонки:

- `Middle`: от 35% до 65% дистанции;
- `Late`: после 70% дистанции.

Это простой и понятный вариант для первой версии отчета. Если нужно, границы фаз можно поменять в строках с `AddRacePhase`.

## 6. Настройка модели данных

После создания `DriverRaceAnalysis`:

1. Нажми `Close & Apply`.
2. Перейди во вкладку `Model view`.
3. Проверь, что в модели есть четыре основные таблицы:
   - `DriverRaceAnalysis`;
   - `drivers`;
   - `constructors`;
   - `races`.
4. Создай связи:
   - `drivers[driver_ID]` -> `DriverRaceAnalysis[driver_ID]`;
   - `constructors[constructor_ID]` -> `DriverRaceAnalysis[constructor_ID]`;
   - `races[race_ID]` -> `DriverRaceAnalysis[race_ID]`.
5. Для каждой связи установи:
   - Cardinality: `One to many (1:*)`;
   - Cross filter direction: `Single`;
   - фильтр должен идти от dimension-таблицы к `DriverRaceAnalysis`.

В итоге должна получиться простая star schema:

```text
drivers          1 -> * DriverRaceAnalysis
constructors     1 -> * DriverRaceAnalysis
races            1 -> * DriverRaceAnalysis
```

Если `results` или `lap_times` все же видны в модели, вернись в Power Query и сними для них `Enable Load`.

## 7. Настройка форматов полей

В `Data view` выбери таблицу `DriverRaceAnalysis` и настрой поля:

- `Middle Relative Pace %` -> формат `Percentage`, 2 знака после запятой.
- `Late Relative Pace %` -> формат `Percentage`, 2 знака после запятой.
- `Late vs Middle Pace Improvement` -> формат `Percentage`, 2 знака после запятой.
- `Position Gain` -> формат `Whole number`.
- `Start Position` -> формат `Whole number`.
- `Finish Position` -> формат `Whole number`.

В таблице `races` настрой:

- `Race Date` -> формат `Date`;
- `Season` -> формат `Whole number`;
- `Round` -> формат `Whole number`.

Для сортировки slicer `Season` от новых сезонов к старым:

1. Выбери колонку `races[Season]`.
2. Нажми `Column tools` -> `Sort by column`.
3. Выбери `races[Season Sort Desc]`.

Для сортировки `Starting Position Group` в порядке `P1-P5`, `P6-P10`, `P11-P15`, `P16+`:

1. Выбери колонку `DriverRaceAnalysis[Starting Position Group]`.
2. Нажми `Column tools` -> `Sort by column`.
3. Выбери `DriverRaceAnalysis[Starting Position Group Sort]`.

Для сортировки bucket-поля:

1. Выбери колонку `DriverRaceAnalysis[Pace Improvement Bucket]`.
2. Нажми `Column tools` -> `Sort by column`.
3. Выбери `DriverRaceAnalysis[Pace Improvement Bucket Sort]`.

`Pace Improvement Bucket` должен показывать понятные бизнес-подписи:

- `Large pace decline`;
- `Medium pace decline`;
- `Small pace decline`;
- `Small pace gain`;
- `Medium pace gain`;
- `Large pace gain`.

Числовые границы этих групп хранятся отдельно в колонке `DriverRaceAnalysis[Pace Improvement Range]`. Используй ее в таблицах и tooltips, когда зрителю нужно видеть точный диапазон.

После настройки сортировки можно скрыть технические sort-колонки из report view:

- `races[Season Sort Desc]`;
- `DriverRaceAnalysis[Starting Position Group Sort]`;
- `DriverRaceAnalysis[Pace Improvement Bucket Sort]`.

## 8. Создание DAX-мер

В Power BI перейди в `Report view`.

1. Правый клик по таблице `DriverRaceAnalysis`.
2. Нажми `New measure`.
3. Создай меры ниже по одной.

### 8.1. Базовые меры

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

### 8.2. KPI для проверки гипотезы

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
Conversion Rate Gap =
[Conversion Rate - Improvers] - [Conversion Rate - Non-Improvers]
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

```dax
Hypothesis Verdict =
VAR ConversionGap = [Conversion Rate Gap]
VAR MedianGainGap = [Position Gain Difference]
RETURN
    SWITCH(
        TRUE(),
        ISBLANK(ConversionGap) || ISBLANK(MedianGainGap), "Not enough data",
        ConversionGap > 0 && MedianGainGap > 0, "Supported in selected context",
        ConversionGap > 0 || MedianGainGap > 0, "Mixed / context-dependent",
        "Not supported in selected context"
    )
```

### 8.3. Мера для каскадных фильтров

Эта мера нужна, чтобы slicers показывали только значения, для которых есть строки в `DriverRaceAnalysis` в текущем контексте фильтров.

```dax
Slicer Has Data =
IF([Observations] > 0, 1, 0)
```

### 8.4. Меры для корректного tooltip в scatter plot

Scatter plot строит точки из fact-таблицы `DriverRaceAnalysis`. Если добавить в tooltip напрямую поля `drivers[Driver]`, `constructors[Constructor]` или `races[Grand Prix]`, Power BI может показать неправильное значение, потому что конкретная точка из fact-таблицы не фильтрует dimension-таблицы обратно.

Чтобы tooltip всегда показывал правильного пилота, команду и гонку для выбранной точки, создай отдельные lookup-меры:

```dax
Tooltip Driver =
VAR DriverID =
    SELECTEDVALUE('DriverRaceAnalysis'[driver_ID])
RETURN
    LOOKUPVALUE(
        drivers[Driver],
        drivers[driver_ID], DriverID
    )
```

```dax
Tooltip Constructor =
VAR ConstructorID =
    SELECTEDVALUE('DriverRaceAnalysis'[constructor_ID])
RETURN
    LOOKUPVALUE(
        constructors[Constructor],
        constructors[constructor_ID], ConstructorID
    )
```

```dax
Tooltip Grand Prix =
VAR RaceID =
    SELECTEDVALUE('DriverRaceAnalysis'[race_ID])
RETURN
    LOOKUPVALUE(
        races[Grand Prix],
        races[race_ID], RaceID
    )
```

```dax
Tooltip Season =
VAR RaceID =
    SELECTEDVALUE('DriverRaceAnalysis'[race_ID])
RETURN
    LOOKUPVALUE(
        races[Season],
        races[race_ID], RaceID
    )
```

Не исправляй эту проблему через bidirectional relationships. Для tooltip надежнее оставить модель со связями `Single direction` и использовать `LOOKUPVALUE`.

### 8.5. Дополнительная мера корреляции

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

## 9. Общие фильтры отчета

На каждую страницу можно добавить slicer-фильтры:

- `races[Season]`;
- `constructors[Constructor]`;
- `drivers[Driver]`;
- `DriverRaceAnalysis[Starting Position Group]`;
- `races[Grand Prix]`.

Для первой версии достаточно двух фильтров:

- `races[Season]`;
- `DriverRaceAnalysis[Starting Position Group]`.

Так отчет будет проще читать.

### 9.1. Как сделать каскадные фильтры

При star schema slicers из разных dimension-таблиц могут показывать полный список значений, даже если для выбранного сезона часть конструкторов или гонок не имеет строк в fact-таблице. Чтобы списки сокращались под текущий выбор, используй меру `Slicer Has Data`.

Для каждого slicer:

1. Выбери slicer, например `constructors[Constructor]`.
2. В панели `Filters` найди блок `Filters on this visual`.
3. Добавь туда меру `Slicer Has Data`.
4. Установи условие:
   - `Slicer Has Data` is `1`.
5. Если в настройках slicer есть `Show items with no data`, выключи его.

Повтори это для slicers:

- `races[Season]`;
- `constructors[Constructor]`;
- `drivers[Driver]`;
- `DriverRaceAnalysis[Starting Position Group]`;
- `races[Grand Prix]`.

После этого выбор `Season = 2025` будет оставлять в списках только конструкторов, пилотов и Гран-при с наблюдениями за 2025 год. Обратная логика тоже будет работать: выбор конструктора или гонки сократит список доступных сезонов.

## 10. Страница 1: Executive Verdict

Цель страницы: сразу показать, подтверждается ли гипотеза.

### 10.1. Добавь заголовок

Добавь текст:

```text
Executive Verdict: Does Late Pace Convert Into Positions?
```

### 10.2. Добавь KPI-карточки

Создай компактный KPI-блок. Лучше сделать две строки карточек: первая строка отвечает на conversion, вторая строка показывает positional outcome.

Первая строка:

1. `Observations`
2. `Conversion Rate - Improvers`
3. `Conversion Rate - Non-Improvers`
4. `Conversion Rate Gap`

Вторая строка:

1. `Median Position Gain - Improvers`
2. `Median Position Gain - Non-Improvers`
3. `Position Gain Difference`
4. `Hypothesis Verdict`

Настройки:

- для `Conversion Rate - Improvers`, `Conversion Rate - Non-Improvers` и `Conversion Rate Gap` используй формат `Percentage`;
- для медианных позиций используй 1 знак после запятой;
- для `Observations` используй целое число;
- подписи карточек сделай короткими:
  - `N`;
  - `Conversion Rate`;
  - `Non-Improver Conv.`;
  - `Conversion Gap`;
  - `Median Gain: Improvers`;
  - `Median Gain: Non-Improvers`;
  - `Median Gain Gap`;
  - `Verdict`.

`Conversion Rate - Improvers` остается главным KPI страницы, но без `Conversion Rate - Non-Improvers` его трудно интерпретировать. `Conversion Rate Gap` сразу показывает, насколько improvers лучше или хуже non-improvers в выбранном контексте.

Если места мало, оставь обязательный минимум:

- `Observations`;
- `Conversion Rate - Improvers`;
- `Conversion Rate - Non-Improvers`;
- `Conversion Rate Gap`;
- `Position Gain Difference`;
- `Hypothesis Verdict`.

### 10.3. Добавь график долей исходов

Используй `100% stacked column chart`.

Поля:

- X-axis: `DriverRaceAnalysis[Late Pace Group]`;
- Legend: `DriverRaceAnalysis[Position Outcome]`;
- Values: `Observations`.

Этот график отвечает на вопрос: у какой группы больше доля `Gained Positions`.

Рекомендуемые настройки:

- включи `Data labels`, чтобы были видны проценты сегментов;
- выключи или переименуй Y-axis title: лучше `Share of observations`, а не `Observations`;
- используй смысловые цвета:
  - `Gained Positions` - зеленый или синий;
  - `Held Position` - серый;
  - `Lost Positions` - красный или оранжевый;
- добавь `Observations` в tooltip, чтобы было видно размер выборки;
- если выбран один Гран-при, обязательно смотри на `Observations`: на маленькой выборке вывод должен быть аккуратным.

### 10.4. Добавь динамический verdict

Добавь `Card` visual с мерой `Hypothesis Verdict`. Она будет меняться при выборе сезона, конструктора, пилота, стартовой группы или Гран-при.

Интерпретация:

- `Supported in selected context` - improvers лучше non-improvers и по conversion rate, и по median position gain;
- `Mixed / context-dependent` - улучшение видно только по одной из двух метрик;
- `Not supported in selected context` - improvers не лучше non-improvers в выбранном срезе;
- `Not enough data` - в выбранном срезе недостаточно данных для вывода.

Если хочешь оставить обычный текстовый блок вместо динамической карточки, используй одну из формулировок:

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

## 11. Страница 2: Evidence & Relationship

Цель страницы: показать форму связи между улучшением темпа и изменением позиции.

### 11.1. Scatter plot

Добавь `Scatter chart`.

Поля:

- X-axis: `DriverRaceAnalysis[Late vs Middle Pace Improvement]`;
- Y-axis: `DriverRaceAnalysis[Position Gain]`;
- Legend: `DriverRaceAnalysis[Position Outcome]`;
- Details: `DriverRaceAnalysis[Observation ID]`;
- Tooltips:
  - `Tooltip Season`;
  - `Tooltip Grand Prix`;
  - `Tooltip Driver`;
  - `Tooltip Constructor`;
  - `DriverRaceAnalysis[Start Position]`;
  - `DriverRaceAnalysis[Finish Position]`;
  - `DriverRaceAnalysis[Middle Relative Pace %]`;
  - `DriverRaceAnalysis[Late Relative Pace %]`.

Важно: для scatter tooltip не добавляй напрямую `races[Season]`, `races[Grand Prix]`, `drivers[Driver]` и `constructors[Constructor]`. Используй lookup-меры `Tooltip Season`, `Tooltip Grand Prix`, `Tooltip Driver`, `Tooltip Constructor`, иначе Power BI может показать первое значение из dimension-таблицы, а не значение, связанное с конкретной точкой.

Настройки:

- X-axis форматируй как процент;
- добавь вертикальную reference line на `0`;
- добавь горизонтальную reference line на `0`;
- точку справа от нуля по X можно читать как улучшение позднего темпа;
- точку выше нуля по Y можно читать как отыгранные позиции.

### 11.2. Bar chart по bucket

Добавь `Clustered column chart`.

Поля:

- X-axis: `DriverRaceAnalysis[Pace Improvement Bucket]`;
- Values: `Median Position Gain`.
- Tooltips:
  - `DriverRaceAnalysis[Pace Improvement Range]`;
  - `Observations`;
  - `% Gained Positions`.

Проверь, что `DriverRaceAnalysis[Pace Improvement Bucket]` отсортирован по `DriverRaceAnalysis[Pace Improvement Bucket Sort]`.

### 11.3. Таблица evidence

Добавь `Table` visual.

Поля:

- `DriverRaceAnalysis[Pace Improvement Bucket]`;
- `DriverRaceAnalysis[Pace Improvement Range]`;
- `Observations`;
- `Median Position Gain`;
- `% Gained Positions`.

Сортировка:

- сортируй по `DriverRaceAnalysis[Pace Improvement Bucket Sort]` по возрастанию.

Главный вопрос этой страницы:

```text
Does stronger late pace improvement usually correspond to better positional outcome?
```

## 12. Страница 3: Strategic Application

Цель страницы: показать, где улучшение позднего темпа полезнее всего для команды.

### 12.1. Conversion Rate by Starting Position Group

Добавь `Clustered column chart`.

Поля:

- X-axis: `DriverRaceAnalysis[Starting Position Group]`;
- Legend: `DriverRaceAnalysis[Late Pace Group]`;
- Values: `% Gained Positions`.

Интерпретация:

- если `Late Pace Improved` выше в конкретной стартовой группе, гипотеза лучше работает именно там;
- если разницы нет, поздний темп в этой группе плохо объясняет изменение позиции.

### 12.2. Рейтинг конструкторов

Добавь `Table` или `Matrix`.

Поля:

- `constructors[Constructor]`;
- `Observations`;
- `Median Late Pace Improvement`;
- `% Gained Positions`;
- `Median Position Gain`.

Рекомендуемый фильтр:

- оставь только конструкторов с достаточным числом наблюдений, например `Observations >= 20`.

Это нужно, чтобы не делать выводы по слишком маленьким выборкам.

### 12.3. 2x2 conversion matrix

Добавь `Matrix` visual.

Поля:

- Rows: `DriverRaceAnalysis[Late Pace Group]`;
- Columns: `DriverRaceAnalysis[Position Gain Flag]`;
- Values: `Observations`.

Матрица показывает четыре сценария:

- `Late Pace Improved` + `Gained Positions` = successful conversion;
- `Late Pace Improved` + `Did Not Gain Positions` = unconverted late pace;
- `Late Pace Did Not Improve` + `Gained Positions` = external / non-pace gain;
- `Late Pace Did Not Improve` + `Did Not Gain Positions` = expected weakness.

### 12.4. Таблица Unconverted Late Pace

Добавь `Table` visual.

Поля:

- `races[Season]`;
- `races[Grand Prix]`;
- `drivers[Driver]`;
- `constructors[Constructor]`;
- `DriverRaceAnalysis[Start Position]`;
- `DriverRaceAnalysis[Finish Position]`;
- `DriverRaceAnalysis[Position Gain]`;
- `DriverRaceAnalysis[Middle Relative Pace %]`;
- `DriverRaceAnalysis[Late Relative Pace %]`;
- `DriverRaceAnalysis[Late vs Middle Pace Improvement]`;
- `DriverRaceAnalysis[Status]`.

Фильтр visual-level:

- `DriverRaceAnalysis[Conversion Quadrant]` = `Unconverted Late Pace`.

Сортировка:

- сортируй по `DriverRaceAnalysis[Late vs Middle Pace Improvement]` по убыванию.

Эта таблица показывает случаи, где темп улучшился, но позиции не были отыграны. Это важный список для стратегического разбора.

## 13. Как читать ключевые метрики

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

## 14. Как сформулировать финальный вывод

Используй такую логику:

1. Сравни `Conversion Rate - Improvers` и `Conversion Rate - Non-Improvers`.
2. Проверь `Conversion Rate Gap`: положительное значение поддерживает гипотезу, отрицательное ослабляет ее.
3. Сравни `Median Position Gain - Improvers` и `Median Position Gain - Non-Improvers`.
4. Проверь `Position Gain Difference`: положительное значение означает, что improvers имеют лучший медианный позиционный результат.
5. Посмотри `Observations`: если выбран один Гран-при или маленький сегмент, вывод должен звучать как локальный.
6. Посмотри scatter plot: есть ли больше точек в правой верхней зоне.
7. Проверь разрезы на странице 3: стартовая группа и конструктор.

Гипотеза поддержана, если:

- у improvers выше conversion rate;
- у improvers выше median position gain;
- связь видна хотя бы в части важных сегментов.

Гипотеза частично поддержана, если:

- общий эффект есть, но он явно зависит от стартовой позиции, команды или сезона.

Гипотеза не поддержана, если:

- improvers не отыгрывают позиции чаще;
- медианный `Position Gain` у improvers не выше.

## 15. Ограничения анализа, которые нужно упомянуть

В финальном комментарии к отчету обязательно укажи:

- отчет показывает связь, но не доказывает причинно-следственную зависимость;
- на изменение позиции влияют пит-стопы, трафик, Safety Car, погода, штрафы, сходы и командная тактика;
- `race_ID` не используется для хронологии, потому что это технический идентификатор;
- период анализа начинается с гонок, где есть lap times, то есть старые сезоны без времен кругов не входят в расчет;
- медиана используется вместо среднего, чтобы снизить влияние очень медленных кругов, пит-стопов и выбросов.

## 16. Финальная проверка перед сдачей

Перед сдачей отчета проверь:

- на странице 1 есть `Observations`, conversion KPI для improvers и non-improvers, `Conversion Rate Gap`, median gain KPI и динамический verdict;
- на странице 2 есть scatter plot, bucket chart и evidence table;
- на странице 3 есть стартовые группы, рейтинг конструкторов, 2x2 matrix и таблица `Unconverted Late Pace`;
- slicers настроены через `Slicer Has Data`, чтобы показывать только значения с доступными наблюдениями;
- проценты отображаются как проценты, а не как десятичные числа;
- `Pace Improvement Bucket` отсортирован в правильном порядке;
- в таблице `DriverRaceAnalysis` одна строка соответствует одному пилоту в одной гонке;
- модель построена как star schema: `drivers`, `constructors` и `races` фильтруют `DriverRaceAnalysis`;
- текстовые поля пилотов, команд и гонок берутся из dimension-таблиц, а не дублируются в `DriverRaceAnalysis`;
- вывод сформулирован аккуратно: late pace improvement может быть индикатором positional gain, но не единственной причиной.
