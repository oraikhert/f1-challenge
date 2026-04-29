# Инструкция по реализации Power BI-дашборда McLaren Miami Race Pace

## 1. Цель дашборда

Построить Power BI-дашборд по задаче из `mclaren_miami_powerbi_task.md`: проверить, может ли McLaren получить преимущество на Гран-при Майами за счет более стабильного гоночного темпа на длинной дистанции по сравнению с Ferrari, Mercedes и Red Bull.

Ключевая идея: сравнивать не только абсолютное время круга, а изменение темпа по ходу гонки относительно основных соперников на том же круге.

## 2. Какие файлы использовать

Использовать только эти файлы из папки `Dataset`:

| Файл | Зачем нужен |
|---|---|
| `Dataset/lap_times.csv` | Факт-таблица кругов: `race_ID`, `driver_ID`, `lap_num`, `position`, `lap_time_ms` |
| `Dataset/results.csv` | Связь пилота с командой в конкретной гонке: `race_ID`, `driver_ID`, `constructor_ID`; также стартовая/финишная позиция |
| `Dataset/races.csv` | Сезон, этап, трасса, дата гонки |
| `Dataset/drivers.csv` | Код и имя пилота для фильтров и tooltip |
| `Dataset/constructors.csv` | Название команды |

Не использовать:

| Файл | Почему не нужен |
|---|---|
| `Dataset/driver_standings.csv` | Накопленные очки пилотов не нужны для анализа стабильности кругов |
| `Dataset/cons_standings.csv` | Накопленные очки команд не нужны для проверки гипотезы по race pace |

Важно: исходные CSV не изменять. Все преобразования выполняются только в Power Query внутри Power BI.

## 3. Период и команды анализа

Период:

- основной фильтр: сезоны `2022-2026`;
- для подготовки к Miami GP 2026 не включать саму гонку Miami 2026, потому что она является целевой будущей гонкой;
- использовать только гонки до Miami 2026: `race_date < #date(2026, 5, 3)`;
- по текущему набору данных последние гонки с результатами перед Miami 2026: Australian GP 2026, Chinese GP 2026, Japanese GP 2026.

Команды для основной гипотезы:

- McLaren;
- Ferrari;
- Mercedes;
- Red Bull.

Похожие трассы для страницы 4:

- Miami Grand Prix;
- Saudi Arabian Grand Prix / Jeddah;
- Azerbaijan Grand Prix / Baku;
- Singapore Grand Prix;
- Las Vegas Grand Prix;
- Monaco Grand Prix.

## 4. Импорт данных в Power BI

1. Открыть Power BI Desktop.
2. Выбрать `Get data` -> `Text/CSV`.
3. Загрузить пять CSV:
   - `lap_times.csv`;
   - `results.csv`;
   - `races.csv`;
   - `drivers.csv`;
   - `constructors.csv`.
4. Нажать `Transform Data`, не `Load`.
5. Переименовать запросы:
   - `stg_lap_times`;
   - `stg_results`;
   - `stg_races`;
   - `stg_drivers`;
   - `stg_constructors`.

Для staging-запросов позже отключить `Enable load`, чтобы в модель загружались только финальные таблицы.

## 5. Power Query: подготовка справочников

### 5.1. `stg_races`

Оставить поля:

- `race_ID`;
- `year`;
- `round`;
- `circuit_ID`;
- `circuit_location`;
- `circuit_country`;
- `circuit_name`;
- `race_date`.

Шаги:

1. Заменить `\N` на `null`.
2. Для `race_date` выбрать `Change Type` -> `Using Locale`:
   - Data type: `Date`;
   - Locale: `English (United Kingdom)`.
3. Для `year`, `round`, `race_ID`, `circuit_ID` установить тип `Whole Number`.
4. Отфильтровать:
   - `year >= 2022`;
   - `race_date < #date(2026, 5, 3)`.
5. Добавить колонку `RaceLabel`:

```powerquery
Text.From([year]) & " " & [circuit_name]
```

6. Добавить колонку `RaceSort`:

```powerquery
[year] * 100 + [round]
```

7. Добавить колонку `CircuitGroup`:

```powerquery
if List.Contains(
    {
        "Miami Grand Prix",
        "Saudi Arabian Grand Prix",
        "Azerbaijan Grand Prix",
        "Singapore Grand Prix",
        "Las Vegas Grand Prix",
        "Monaco Grand Prix"
    },
    [circuit_name]
)
then "Miami / similar street"
else "Other modern races"
```

### 5.2. `stg_constructors`

Оставить поля:

- `constructor_ID`;
- `constructor_ref`;
- `constructor_name`.

Отфильтровать `constructor_name`:

- `McLaren`;
- `Ferrari`;
- `Mercedes`;
- `Red Bull`.

### 5.3. `stg_drivers`

Оставить поля:

- `driver_ID`;
- `driver_ref`;
- `driver_code`;
- `driver_forename`;
- `driver_surname`;
- `driver_nationality`.

Добавить колонку `DriverName`:

```powerquery
[driver_forename] & " " & [driver_surname]
```

### 5.4. `stg_results`

Оставить поля:

- `race_ID`;
- `driver_ID`;
- `constructor_ID`;
- `starting_position`;
- `race_position`;
- `total_laps`;
- `status`.

Шаги:

1. Установить типы `Whole Number` для ID и позиций.
2. Сделать `Merge Queries` с `stg_races` по `race_ID`, тип соединения `Inner`.
3. Сделать `Merge Queries` с `stg_constructors` по `constructor_ID`, тип соединения `Inner`.
4. После merge оставить только строки выбранных четырех команд и выбранного периода.

## 6. Power Query: факт-таблица кругов

### 6.1. Подготовить `stg_lap_times`

Оставить поля:

- `race_ID`;
- `driver_ID`;
- `lap_num`;
- `position`;
- `lap_time_ms`.

Шаги:

1. Установить тип `Whole Number` для `race_ID`, `driver_ID`, `lap_num`, `position`, `lap_time_ms`.
2. Удалить строки, где `lap_time_ms` пустой или равен `0`.
3. Добавить колонку `lap_time_sec`:

```powerquery
Number.From([lap_time_ms]) / 1000
```

### 6.2. Создать таблицу дистанции гонки

Создать reference от `stg_lap_times` и назвать `stg_race_distance`.

Сгруппировать по `race_ID`:

```powerquery
= Table.Group(
    stg_lap_times,
    {"race_ID"},
    {{"RaceDistanceLaps", each List.Max([lap_num]), Int64.Type}}
)
```

Эта таблица нужна, чтобы корректно разделить гонку на фазы Early / Mid / Late.

### 6.3. Создать `FactLapBase`

Создать reference от `stg_lap_times` и назвать `FactLapBase`.

Шаги:

1. Сделать `Merge Queries` с `stg_results` по двум колонкам:
   - `race_ID`;
   - `driver_ID`.
2. Тип соединения: `Inner`.
3. Развернуть из `stg_results`:
   - `constructor_ID`;
   - `starting_position`;
   - `race_position`;
   - `total_laps`;
   - `status`.
4. Сделать merge с `stg_races` по `race_ID`; развернуть:
   - `year`;
   - `round`;
   - `circuit_name`;
   - `circuit_location`;
   - `circuit_country`;
   - `race_date`;
   - `RaceLabel`;
   - `RaceSort`;
   - `CircuitGroup`.
5. Сделать merge с `stg_constructors` по `constructor_ID`; развернуть:
   - `constructor_name`;
   - `constructor_ref`.
6. Сделать merge с `stg_drivers` по `driver_ID`; развернуть:
   - `driver_code`;
   - `DriverName`.
7. Сделать merge с `stg_race_distance` по `race_ID`; развернуть:
   - `RaceDistanceLaps`.

### 6.4. Добавить фазы гонки

В `FactLapBase` добавить колонку `RaceProgress`:

```powerquery
Number.From([lap_num]) / Number.From([RaceDistanceLaps])
```

Добавить колонку `RacePhase`:

```powerquery
if [RaceProgress] <= 0.25 then "Early"
else if [RaceProgress] <= 0.75 then "Mid"
else "Late"
```

Добавить колонку `PhaseSort`:

```powerquery
if [RacePhase] = "Early" then 1
else if [RacePhase] = "Mid" then 2
else 3
```

Примечание: в постановке метрика Pace Drift описана как сравнение первой и последней трети, а страница 3 задает фазы 25% / 50% / 25%. Для единого дашборда использовать фазы страницы 3: Early = первые 25%, Late = последние 25%. Если потребуется строго следовать формуле третей, заменить пороги на `0.3333` и `0.6667`.

## 7. Power Query: Relative Pace Delta и чистые круги

### 7.1. Создать бенчмарк круга

Создать reference от `FactLapBase` и назвать `LapBenchmark`.

Сгруппировать по `race_ID` и `lap_num`:

```powerquery
= Table.Group(
    FactLapBase,
    {"race_ID", "lap_num"},
    {
        {"LapBenchmarkSec", each List.Median([lap_time_sec]), type number},
        {"LapSampleSize", each Table.RowCount(_), Int64.Type}
    }
)
```

`LapBenchmarkSec` - медианное время выбранных топ-команд на конкретном круге конкретной гонки.

### 7.2. Создать медианный бенчмарк гонки

Создать reference от `LapBenchmark` и назвать `RaceBenchmark`.

Сгруппировать по `race_ID`:

```powerquery
= Table.Group(
    LapBenchmark,
    {"race_ID"},
    {{"RaceBenchmarkMedianSec", each List.Median([LapBenchmarkSec]), type number}}
)
```

Эта таблица нужна для пометки глобально медленных кругов, например safety car / virtual safety car.

### 7.3. Создать финальную таблицу `FactLapPace`

Создать reference от `FactLapBase` и назвать `FactLapPace`.

Шаги:

1. Сделать merge с `LapBenchmark` по:
   - `race_ID`;
   - `lap_num`.
2. Развернуть:
   - `LapBenchmarkSec`;
   - `LapSampleSize`.
3. Сделать merge с `RaceBenchmark` по `race_ID`.
4. Развернуть:
   - `RaceBenchmarkMedianSec`.
5. Добавить колонку `RelativePaceDeltaSec`:

```powerquery
[lap_time_sec] - [LapBenchmarkSec]
```

Интерпретация:

- отрицательное значение: быстрее медианы топ-команд на этом круге;
- положительное значение: медленнее медианы топ-команд на этом круге;
- около нуля: на уровне бенчмарка.

### 7.4. Добавить флаг качества круга

Добавить колонку `LapQuality`:

```powerquery
if [lap_num] = 1 then "Start lap"
else if [LapSampleSize] < 4 then "Small benchmark sample"
else if Number.Abs([RelativePaceDeltaSec]) > 10 then "Individual outlier / pit lap"
else if [LapBenchmarkSec] > [RaceBenchmarkMedianSec] * 1.10 then "Global slow lap"
else "Clean"
```

Добавить колонку `IsCleanLap`:

```powerquery
[LapQuality] = "Clean"
```

Почему так:

- первый круг убирается, потому что стартовая процедура и трафик искажают pace;
- индивидуальные выбросы больше 10 секунд от медианы круга обычно означают pit lap, ошибку, повреждение или сильный трафик;
- глобально медленные круги отсекают safety car-подобные ситуации;
- `LapSampleSize < 4` защищает от сравнения, когда на круге осталось слишком мало представителей топ-команд.

Порог `10 секунд` и `10%` можно вынести в Power BI What-if parameters, но для первой версии дашборда оставить фиксированными.

## 8. Финальная модель данных

Загрузить в модель:

- `FactLapPace`;
- `DimRace`;
- `DimConstructor`;
- `DimDriver`.

Создать dimension tables:

### `DimRace`

Reference от `stg_races`.

Оставить:

- `race_ID`;
- `year`;
- `round`;
- `circuit_ID`;
- `circuit_name`;
- `circuit_location`;
- `circuit_country`;
- `race_date`;
- `RaceLabel`;
- `RaceSort`;
- `CircuitGroup`.

Опционально оставить только гонки, которые есть в `FactLapPace`, через inner merge с distinct `race_ID` из `FactLapPace`.

### `DimConstructor`

Reference от `stg_constructors`.

Оставить:

- `constructor_ID`;
- `constructor_ref`;
- `constructor_name`.

### `DimDriver`

Reference от `stg_drivers`.

Оставить:

- `driver_ID`;
- `driver_ref`;
- `driver_code`;
- `DriverName`;
- `driver_nationality`.

### Связи

В `Model view` создать связи:

| From | To | Cardinality | Cross filter |
|---|---|---|---|
| `DimRace[race_ID]` | `FactLapPace[race_ID]` | One-to-many | Single |
| `DimConstructor[constructor_ID]` | `FactLapPace[constructor_ID]` | One-to-many | Single |
| `DimDriver[driver_ID]` | `FactLapPace[driver_ID]` | One-to-many | Single |

Отключить загрузку (`Enable load`) для:

- `stg_lap_times`;
- `stg_results`;
- `stg_races`;
- `stg_drivers`;
- `stg_constructors`;
- `stg_race_distance`;
- `FactLapBase`;
- `LapBenchmark`;
- `RaceBenchmark`.

Сортировки:

- `DimRace[RaceLabel]` сортировать по `DimRace[RaceSort]`;
- `FactLapPace[RacePhase]` сортировать по `FactLapPace[PhaseSort]`.

## 9. DAX-меры

Создать отдельную таблицу `Measures` через `Enter data` с одной пустой колонкой или хранить меры в `FactLapPace`.

### 9.1. Базовые метрики

```DAX
Clean Lap Count :=
CALCULATE(
    COUNTROWS(FactLapPace),
    FactLapPace[IsCleanLap] = TRUE()
)
```

```DAX
Average Lap Time Sec :=
CALCULATE(
    AVERAGE(FactLapPace[lap_time_sec]),
    FactLapPace[IsCleanLap] = TRUE()
)
```

```DAX
Median Lap Time Sec :=
CALCULATE(
    MEDIAN(FactLapPace[lap_time_sec]),
    FactLapPace[IsCleanLap] = TRUE()
)
```

```DAX
Average Relative Pace Sec :=
CALCULATE(
    AVERAGE(FactLapPace[RelativePaceDeltaSec]),
    FactLapPace[IsCleanLap] = TRUE()
)
```

```DAX
Median Relative Pace Sec :=
CALCULATE(
    MEDIAN(FactLapPace[RelativePaceDeltaSec]),
    FactLapPace[IsCleanLap] = TRUE()
)
```

### 9.2. Race phase metrics

```DAX
Early Race Pace Sec :=
AVERAGEX(
    VALUES(DimRace[race_ID]),
    CALCULATE(
        [Median Relative Pace Sec],
        FactLapPace[RacePhase] = "Early"
    )
)
```

```DAX
Late Race Pace Sec :=
AVERAGEX(
    VALUES(DimRace[race_ID]),
    CALCULATE(
        [Median Relative Pace Sec],
        FactLapPace[RacePhase] = "Late"
    )
)
```

```DAX
Pace Drift Sec :=
VAR EarlyPace = [Early Race Pace Sec]
VAR LatePace = [Late Race Pace Sec]
RETURN
IF(
    NOT ISBLANK(EarlyPace) && NOT ISBLANK(LatePace),
    LatePace - EarlyPace
)
```

`Pace Drift Sec` здесь считается по относительному темпу, а не по абсолютному времени круга. Это лучше для сравнения разных трасс: отрицательное значение означает, что команда стала быстрее относительно бенчмарка к концу гонки; положительное - что команда просела относительно соперников.

```DAX
Late Race Advantage Sec :=
[Pace Drift Sec]
```

### 9.3. Стабильность

```DAX
Team Consistency Index Sec :=
AVERAGEX(
    VALUES(DimRace[race_ID]),
    CALCULATE(
        STDEV.P(FactLapPace[RelativePaceDeltaSec]),
        FactLapPace[IsCleanLap] = TRUE()
    )
)
```

```DAX
Pace IQR Sec :=
AVERAGEX(
    VALUES(DimRace[race_ID]),
    VAR Q1 =
        CALCULATE(
            PERCENTILEX.INC(
                FactLapPace,
                FactLapPace[RelativePaceDeltaSec],
                0.25
            ),
            FactLapPace[IsCleanLap] = TRUE()
        )
    VAR Q3 =
        CALCULATE(
            PERCENTILEX.INC(
                FactLapPace,
                FactLapPace[RelativePaceDeltaSec],
                0.75
            ),
            FactLapPace[IsCleanLap] = TRUE()
        )
    RETURN
    Q3 - Q1
)
```

Для основной карточки использовать `Team Consistency Index Sec`. `Pace IQR Sec` можно добавить как альтернативную устойчивую метрику.

Обе меры считаются как среднее по гонкам, чтобы длинные гонки с большим числом чистых кругов не получали непропорционально большой вес.

### 9.4. Rolling average для линии темпа

```DAX
Rolling Relative Pace 5 Laps Sec :=
VAR CurrentLap = MAX(FactLapPace[lap_num])
RETURN
AVERAGEX(
    FILTER(
        ALLSELECTED(FactLapPace[lap_num]),
        FactLapPace[lap_num] <= CurrentLap
            && FactLapPace[lap_num] > CurrentLap - 5
    ),
    [Median Relative Pace Sec]
)
```

Эту меру использовать на странице `Race Pace Evolution`, чтобы линия была менее шумной.

### 9.5. Позиция по фазам гонки

```DAX
Early Avg Position :=
AVERAGEX(
    VALUES(DimRace[race_ID]),
    CALCULATE(
        MEDIAN(FactLapPace[position]),
        FactLapPace[RacePhase] = "Early",
        FactLapPace[IsCleanLap] = TRUE()
    )
)
```

```DAX
Late Avg Position :=
AVERAGEX(
    VALUES(DimRace[race_ID]),
    CALCULATE(
        MEDIAN(FactLapPace[position]),
        FactLapPace[RacePhase] = "Late",
        FactLapPace[IsCleanLap] = TRUE()
    )
)
```

```DAX
Position Gain Late vs Early :=
[Early Avg Position] - [Late Avg Position]
```

Положительное значение означает, что команда в среднем улучшила позицию к концу гонки.

### 9.6. Ранги и статус гипотезы

```DAX
Pace Drift Rank :=
RANKX(
    ALL(DimConstructor[constructor_name]),
    [Pace Drift Sec],
    ,
    ASC,
    Dense
)
```

```DAX
Consistency Rank :=
RANKX(
    ALL(DimConstructor[constructor_name]),
    [Team Consistency Index Sec],
    ,
    ASC,
    Dense
)
```

```DAX
Late Race Pace Rank :=
RANKX(
    ALL(DimConstructor[constructor_name]),
    [Late Race Pace Sec],
    ,
    ASC,
    Dense
)
```

```DAX
McLaren Pace Drift Sec :=
CALCULATE(
    [Pace Drift Sec],
    REMOVEFILTERS(DimConstructor),
    DimConstructor[constructor_name] = "McLaren"
)
```

```DAX
McLaren Consistency Index Sec :=
CALCULATE(
    [Team Consistency Index Sec],
    REMOVEFILTERS(DimConstructor),
    DimConstructor[constructor_name] = "McLaren"
)
```

```DAX
McLaren Late Race Pace Rank :=
CALCULATE(
    [Late Race Pace Rank],
    REMOVEFILTERS(DimConstructor),
    DimConstructor[constructor_name] = "McLaren"
)
```

```DAX
Hypothesis Status :=
VAR DriftRank =
    CALCULATE(
        [Pace Drift Rank],
        REMOVEFILTERS(DimConstructor),
        DimConstructor[constructor_name] = "McLaren"
    )
VAR ConsistencyRank =
    CALCULATE(
        [Consistency Rank],
        REMOVEFILTERS(DimConstructor),
        DimConstructor[constructor_name] = "McLaren"
    )
VAR LateAdvantage =
    CALCULATE(
        [Late Race Advantage Sec],
        REMOVEFILTERS(DimConstructor),
        DimConstructor[constructor_name] = "McLaren"
    )
VAR Score =
    IF(DriftRank <= 2, 1, 0)
        + IF(ConsistencyRank <= 2, 1, 0)
        + IF(LateAdvantage < 0, 1, 0)
RETURN
SWITCH(
    TRUE(),
    Score = 3, "Confirmed",
    Score = 2, "Partially Confirmed",
    "Rejected"
)
```

Логика статуса:

- `Confirmed`: McLaren входит в топ-2 по drift, топ-2 по consistency и улучшает относительный темп в Late phase;
- `Partially Confirmed`: выполняются два условия из трех;
- `Rejected`: выполняется меньше двух условий.

## 10. Страницы дашборда

### Page 1 - Executive Summary

Цель: сразу ответить, подтверждается ли гипотеза.

Фильтры страницы:

- `DimRace[year]`: 2022-2026;
- `DimConstructor[constructor_name]`: McLaren, Ferrari, Mercedes, Red Bull;
- `FactLapPace[IsCleanLap]`: True.

Рекомендуемый основной срез:

- для Miami-анализа: `DimRace[circuit_name] = Miami Grand Prix`;
- для расширенного контекста: `DimRace[CircuitGroup] = Miami / similar street`.

Визуалы:

1. Card: `McLaren Pace Drift Sec`.
2. Card: `McLaren Consistency Index Sec`.
3. Card: `McLaren Late Race Pace Rank`.
4. Card или multi-row card: `Hypothesis Status`.
5. Clustered bar chart:
   - Axis: `DimConstructor[constructor_name]`;
   - Values: `Pace Drift Sec`;
   - Sort: ascending;
   - Interpretation: ниже лучше.
6. Clustered bar chart:
   - Axis: `DimConstructor[constructor_name]`;
   - Values: `Team Consistency Index Sec`;
   - Sort: ascending;
   - Interpretation: ниже стабильнее.
7. Маленькая table:
   - `constructor_name`;
   - `Pace Drift Sec`;
   - `Team Consistency Index Sec`;
   - `Late Race Pace Rank`;
   - `Position Gain Late vs Early`.

Дизайн:

- McLaren выделить цветом `#FF8000`;
- Ferrari `#DC0000`;
- Mercedes `#00A19C`;
- Red Bull `#1E41FF`.

### Page 2 - Race Pace Evolution

Цель: показать, как меняется относительный темп по кругам.

Фильтры:

- `DimRace[year]`;
- `DimRace[circuit_name]`;
- `DimRace[RaceLabel]`;
- `DimConstructor[constructor_name]`;
- `DimDriver[driver_code]`;
- `FactLapPace[IsCleanLap] = True`.

Визуалы:

1. Line chart:
   - X-axis: `FactLapPace[lap_num]`;
   - Y-axis: `Rolling Relative Pace 5 Laps Sec`;
   - Legend: `DimConstructor[constructor_name]`;
   - Tooltip: `Median Relative Pace Sec`, `Clean Lap Count`, `RacePhase`.
2. Secondary line chart по пилотам McLaren:
   - X-axis: `lap_num`;
   - Y-axis: `Rolling Relative Pace 5 Laps Sec`;
   - Legend: `DimDriver[driver_code]`;
   - Visual-level filter: `constructor_name = McLaren`.

Как читать:

- линия ниже нуля означает, что команда быстрее медианного бенчмарка топ-команд;
- если линия McLaren идет вниз к концу гонки, McLaren улучшает относительный темп;
- если линия McLaren растет вверх, темп ухудшается относительно соперников.

### Page 3 - Race Phases Comparison

Цель: сравнить Early / Mid / Late и проверить, меньше ли McLaren проседает к концу гонки.

Визуалы:

1. Clustered bar chart:
   - X-axis: `FactLapPace[RacePhase]`;
   - Values: `Median Relative Pace Sec`;
   - Legend: `DimConstructor[constructor_name]`;
   - Sort `RacePhase` by `PhaseSort`.
2. Matrix:
   - Rows: `DimConstructor[constructor_name]`;
   - Columns: `FactLapPace[RacePhase]`;
   - Values: `Median Relative Pace Sec`.
3. Slope-style line chart:
   - X-axis: `RacePhase`;
   - Y-axis: `Median Relative Pace Sec`;
   - Legend: `constructor_name`.
4. Tooltip page для McLaren:
   - `DimDriver[driver_code]`;
   - `Median Relative Pace Sec`;
   - `Position Gain Late vs Early`;
   - `Clean Lap Count`.

Акцент в выводе:

- McLaren подтверждает гипотезу, если Late phase лучше Early phase относительно Ferrari, Mercedes и Red Bull;
- если Late phase у McLaren хуже или нестабильнее, гипотеза ослабляется.

### Page 4 - Miami vs Similar Circuits

Цель: понять, Майами является отдельным случаем или частью более широкой закономерности на похожих трассах.

Фильтр страницы:

- `DimRace[CircuitGroup] = Miami / similar street`.

Визуалы:

1. Scatter plot:
   - X-axis: `Average Relative Pace Sec`;
   - Y-axis: `Team Consistency Index Sec`;
   - Details: `DimRace[circuit_name]`;
   - Legend: `DimConstructor[constructor_name]`;
   - Size: `Clean Lap Count`.
2. Bar chart:
   - Axis: `DimRace[circuit_name]`;
   - Values: `Pace Drift Sec`;
   - Visual-level filter: `constructor_name = McLaren`;
   - Sort: ascending.
3. Table:
   - `circuit_name`;
   - `RaceLabel`;
   - `Pace Drift Sec`;
   - `Team Consistency Index Sec`;
   - `Late Race Pace Sec`;
   - `Clean Lap Count`;
   - filter: `constructor_name = McLaren`.
4. Small multiples bar chart:
   - Axis: `constructor_name`;
   - Values: `Pace Drift Sec`;
   - Small multiples: `circuit_name`.

Как читать:

- нижний левый сектор scatter plot лучше: быстрый и стабильный относительный темп;
- если McLaren чаще находится ниже конкурентов по variability и pace drift на похожих трассах, гипотеза получает дополнительную поддержку.

## 11. Финальные проверки перед презентацией

Проверить в Power BI:

1. В модель не загружены `driver_standings.csv` и `cons_standings.csv`.
2. В модель загружены только `FactLapPace`, `DimRace`, `DimConstructor`, `DimDriver`.
3. Miami 2026 не попал в анализ, потому что это будущая целевая гонка.
4. В `FactLapPace` есть только команды McLaren, Ferrari, Mercedes, Red Bull.
5. `RacePhase` отсортирован как Early -> Mid -> Late.
6. `RaceLabel` отсортирован по `RaceSort`, а не по алфавиту.
7. Все основные визуалы используют только `IsCleanLap = True`.
8. В Page 2 выбран один `RaceLabel` или один `circuit_name`, иначе линии по lap number будут смешивать разные гонки.
9. Отрицательный `RelativePaceDeltaSec` подписан как better/faster, чтобы зритель не перепутал направление метрики.
10. Карточка `Hypothesis Status` сверена вручную с графиками Page 1 и Page 3.

## 12. Рекомендуемый короткий сценарий защиты

1. Page 1: показать статус гипотезы и два главных сравнения - `Pace Drift` и `Consistency Index`.
2. Page 2: объяснить динамику по кругам: становится ли McLaren сильнее во второй половине гонки.
3. Page 3: показать Early / Mid / Late и связать изменение темпа с позициями.
4. Page 4: расширить вывод с Miami на похожие трассы и показать, является ли паттерн устойчивым.

Финальная формулировка вывода должна зависеть от результата в Power BI:

- если McLaren имеет лучший или топ-2 `Pace Drift`, низкий `Consistency Index` и отрицательный `Late Race Advantage`, гипотеза подтверждается;
- если выполняются только два условия, гипотеза подтверждается частично;
- если McLaren не лучше конкурентов по drift и consistency, гипотеза отклоняется.
