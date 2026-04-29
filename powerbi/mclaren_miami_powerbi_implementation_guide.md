# Инструкция по реализации Power BI-дашборда McLaren Miami Race Pace

## 1. Цель дашборда

Построить Power BI-дашборд по задаче из `mclaren_miami_powerbi_task.md`: проверить, может ли McLaren получить преимущество на Гран-при Майами за счет более стабильного наблюдаемого гоночного темпа на длинной дистанции по сравнению с Ferrari, Mercedes и Red Bull.

Ключевая идея: сравнивать не только абсолютное время круга, а изменение темпа по ходу гонки относительно основных соперников на том же круге.

Важно: дашборд анализирует именно `lap_time_ms` и производные метрики по очищенным кругам. В нем нельзя делать выводы о чистой деградации шин, эффективности пит-стопов, DRS или погодных факторах, потому что таких данных нет в доступной модели.

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

## 3.1. Ограничения данных и правила интерпретации

В отчете обязательно явно зафиксировать ограничения модели данных.

| Отсутствующий фактор | Риск для анализа | Как учитывать в Power BI |
|---|---|---|
| Tyres: состав и возраст комплекта | Нельзя отделить деградацию шин от других причин изменения темпа | Использовать термин `Observed Pace Drift`, не `Tyre Degradation` |
| Pit stops | In-lap / out-lap могут выглядеть как резкое падение темпа | Исключать индивидуальные выбросы относительно rolling median пилота |
| Weather | Дождь, температура и ветер могут менять темп всех команд | Сравнивать команды внутри одной гонки и одного круга через `RelativePaceDeltaSec` |
| DRS | Ускорение или обгон нельзя объяснить DRS-эффектом | Не делать выводы о DRS; позицию использовать только как контекст |
| Safety Car / VSC | Нейтрализация резко увеличивает время круга у всего поля | Помечать field-wide spikes и исключать их из основных pace-метрик |
| Traffic / battles | Отдельный круг может быть медленным из-за борьбы на трассе | Использовать медианы, rolling average и сравнение по фазам |

Правила формулировки выводов:

1. Говорить: "McLaren показывает более стабильный наблюдаемый гоночный темп по очищенным lap-time данным".
2. Не говорить: "McLaren лучше работает с шинами", "стратегия пит-стопов эффективнее" или "DRS дает преимущество".
3. Основные выводы делать по clean laps; сырые круги использовать только для проверки устойчивости результата.
4. Если преимущество McLaren исчезает после очистки аномальных кругов, статус гипотезы должен быть не выше `Partially Confirmed`.
5. На отдельной странице `Data Quality & Methodology` показать, сколько кругов исключено, почему они исключены и насколько KPI меняются до / после очистки.

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

В staging-запросе не фильтровать команды до четырех основных: полный список команд нужен для field-wide spike detection по всему пелотону.

Добавить колонку `IsCoreCompetitor`:

```powerquery
List.Contains(
    {"McLaren", "Ferrari", "Mercedes", "Red Bull"},
    [constructor_name]
)
```

Основные команды для аналитических страниц:

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
4. Развернуть из `stg_constructors`:
   - `constructor_name`;
   - `constructor_ref`;
   - `IsCoreCompetitor`.
5. Не фильтровать `IsCoreCompetitor` на этом шаге. Фильтрация до McLaren / Ferrari / Mercedes / Red Bull выполняется только в финальной `FactLapPace`, после расчета quality flags.

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
   - `constructor_ref`;
   - `IsCoreCompetitor`.
6. Сделать merge с `stg_drivers` по `driver_ID`; развернуть:
   - `driver_code`;
   - `DriverName`.
7. Сделать merge с `stg_race_distance` по `race_ID`; развернуть:
   - `RaceDistanceLaps`.

`FactLapBase` на этом этапе содержит все команды современного периода. Это нужно, чтобы корректно находить field-wide spikes по всему пелотону. Основные визуалы позже используют только строки с `IsCoreCompetitor = true`.

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

Примечание: в постановке метрика `Observed Pace Drift` описана как сравнение первой и последней трети, а страница 3 задает фазы 25% / 50% / 25%. Для единого дашборда использовать фазы страницы 3: Early = первые 25%, Late = последние 25%. Если потребуется строго следовать формуле третей, заменить пороги на `0.3333` и `0.6667`.

## 7. Power Query: Relative Pace Delta и чистые круги

### 7.1. Создать бенчмарк круга

Создать reference от `FactLapBase` и назвать `LapBenchmark`.

Перед группировкой отфильтровать `IsCoreCompetitor = true`, потому что `RelativePaceDeltaSec` должен сравнивать McLaren с Ferrari, Mercedes и Red Bull, а не со всем пелотоном.

Сгруппировать по `race_ID` и `lap_num`:

```powerquery
= Table.Group(
    Table.SelectRows(FactLapBase, each [IsCoreCompetitor] = true),
    {"race_ID", "lap_num"},
    {
        {"LapBenchmarkSec", each List.Median([lap_time_sec]), type number},
        {"LapSampleSize", each Table.RowCount(_), Int64.Type}
    }
)
```

`LapBenchmarkSec` - медианное время выбранных основных команд на конкретном круге конкретной гонки.

### 7.2. Создать field-wide benchmark для поиска нейтрализованных кругов

Создать reference от `FactLapBase` и назвать `FieldLapBenchmark`.

Сгруппировать по `race_ID` и `lap_num` без фильтра по командам:

```powerquery
= Table.Group(
    FactLapBase,
    {"race_ID", "lap_num"},
    {
        {"FieldMedianLapSec", each List.Median([lap_time_sec]), type number},
        {"FieldLapSampleSize", each Table.RowCount(_), Int64.Type}
    }
)
```

Создать reference от `FieldLapBenchmark` и назвать `RaceFieldBenchmark`.

Сгруппировать по `race_ID`:

```powerquery
= Table.Group(
    FieldLapBenchmark,
    {"race_ID"},
    {{"RaceFieldMedianSec", each List.Median([FieldMedianLapSec]), type number}}
)
```

Эти таблицы нужны для пометки кругов, где замедлился почти весь пелотон, например Safety Car / VSC или сильное изменение условий.

### 7.3. Создать rolling median пилота

Создать reference от `FactLapBase` и назвать `FactLapPace`.

Добавить rolling median по каждому пилоту в каждой гонке. В Advanced Editor можно использовать такой шаблон:

```powerquery
let
    Source = FactLapBase,
    Sorted = Table.Sort(
        Source,
        {
            {"race_ID", Order.Ascending},
            {"driver_ID", Order.Ascending},
            {"lap_num", Order.Ascending}
        }
    ),
    Grouped = Table.Group(
        Sorted,
        {"race_ID", "driver_ID"},
        {
            {
                "Rows",
                (t as table) as table =>
                    let
                        Indexed = Table.AddIndexColumn(t, "DriverLapIndex", 0, 1, Int64.Type),
                        Times = Indexed[lap_time_sec],
                        WithMedian = Table.AddColumn(
                            Indexed,
                            "DriverRollingMedianSec",
                            (r as record) =>
                                let
                                    i = r[DriverLapIndex],
                                    start = Number.Max(0, i - 2),
                                    count = Number.Min(5, List.Count(Times) - start),
                                    window = List.RemoveNulls(List.Range(Times, start, count))
                                in
                                    if List.Count(window) >= 3 then List.Median(window) else null,
                            type number
                        )
                    in
                        WithMedian,
                type table
            }
        }
    ),
    Expanded = Table.ExpandTableColumn(
        Grouped,
        "Rows",
        List.RemoveItems(
            Table.ColumnNames(Source) & {"DriverLapIndex", "DriverRollingMedianSec"},
            {"race_ID", "driver_ID"}
        )
    )
in
    Expanded
```

Rolling window 5 laps достаточно сглаживает обычный шум, но сохраняет резкие индивидуальные выбросы: pit lap, повреждение, ошибка, трафик или другой аномальный круг.

### 7.4. Добавить бенчмарки в `FactLapPace`

Шаги:

1. Сделать merge с `LapBenchmark` по:
   - `race_ID`;
   - `lap_num`.
2. Развернуть:
   - `LapBenchmarkSec`;
   - `LapSampleSize`.
3. Сделать merge с `FieldLapBenchmark` по:
   - `race_ID`;
   - `lap_num`.
4. Развернуть:
   - `FieldMedianLapSec`;
   - `FieldLapSampleSize`.
5. Сделать merge с `RaceFieldBenchmark` по `race_ID`.
6. Развернуть:
   - `RaceFieldMedianSec`.
7. Добавить колонку `RelativePaceDeltaSec`:

```powerquery
[lap_time_sec] - [LapBenchmarkSec]
```

Интерпретация:

- отрицательное значение: быстрее медианы топ-команд на этом круге;
- положительное значение: медленнее медианы топ-команд на этом круге;
- около нуля: на уровне бенчмарка.

### 7.5. Добавить флаги качества круга

Добавить колонку `IsStartLap`:

```powerquery
[lap_num] = 1
```

Добавить колонку `DriverRollingDeltaSec`:

```powerquery
if [DriverRollingMedianSec] = null
then null
else [lap_time_sec] - [DriverRollingMedianSec]
```

Добавить колонку `FieldSpikeRatio`:

```powerquery
if [RaceFieldMedianSec] = null
then null
else [FieldMedianLapSec] / [RaceFieldMedianSec]
```

Добавить колонку `IsExtremeLapTime`:

```powerquery
[lap_time_sec] < 60
    or ([RaceFieldMedianSec] <> null and [lap_time_sec] > [RaceFieldMedianSec] * 1.35)
```

Добавить колонку `IsFieldWideSpike`:

```powerquery
[FieldSpikeRatio] <> null and [FieldSpikeRatio] > 1.10
```

Добавить колонку `IsDriverRollingOutlier`:

```powerquery
[DriverRollingDeltaSec] <> null
    and Number.Abs([DriverRollingDeltaSec]) > 8
```

Добавить колонку `LapQuality`:

```powerquery
if [IsStartLap] then "Start lap"
else if [LapSampleSize] < 4 then "Small competitor benchmark sample"
else if [IsExtremeLapTime] then "Extreme lap time"
else if [IsFieldWideSpike] then "Field-wide spike"
else if [IsDriverRollingOutlier] then "Driver rolling outlier / pit lap"
else "Clean"
```

Добавить колонку `IsCleanLap`:

```powerquery
[LapQuality] = "Clean"
```

Почему так:

- первый круг убирается, потому что стартовая процедура и трафик искажают pace;
- индивидуальные выбросы больше 8 секунд от rolling median пилота обычно означают pit lap, ошибку, повреждение или сильный трафик;
- field-wide spikes отсекают Safety Car / VSC-подобные ситуации, потому что сравниваются с медианой всего пелотона;
- экстремальные `lap_time_ms` защищают от технических артефактов и кругов, явно не похожих на гоночный темп;
- `LapSampleSize < 4` защищает от сравнения, когда на круге осталось слишком мало представителей топ-команд.

Пороги `8 секунд`, `10%` и `1.35x` можно вынести в Power BI What-if parameters, но для первой версии дашборда оставить фиксированными.

`Start lap` хранится отдельной причиной качества, чтобы на странице `Data Quality & Methodology` можно было отдельно показать влияние настройки "exclude first lap". В первой версии `IsCleanLap = false` для первого круга.

После добавления quality flags отфильтровать `FactLapPace`:

```powerquery
[IsCoreCompetitor] = true
```

Так финальная таблица содержит только McLaren, Ferrari, Mercedes и Red Bull, но `FieldMedianLapSec` и `RaceFieldMedianSec` были рассчитаны по всему пелотону.

## 8. Финальная модель данных

Загрузить в модель:

- `FactLapPace`;
- `DimRace`;
- `DimConstructor`;
- `DimDriver`;
- `DimLapQualityRule`;
- `DimLapViewMode`.

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

Отфильтровать:

```powerquery
[IsCoreCompetitor] = true
```

Оставить:

- `constructor_ID`;
- `constructor_ref`;
- `constructor_name`;
- `IsCoreCompetitor`.

### `DimDriver`

Reference от `stg_drivers`.

Оставить:

- `driver_ID`;
- `driver_ref`;
- `driver_code`;
- `DriverName`;
- `driver_nationality`.

### `DimLapQualityRule`

Создать через `Blank Query` и назвать `DimLapQualityRule`.

Код:

```powerquery
= #table(
    type table [
        LapQuality = text,
        LapQualitySort = Int64.Type,
        CleaningRule = text,
        Interpretation = text,
        DefaultAction = text
    ],
    {
        {
            "Clean",
            1,
            "Круг прошел все проверки качества",
            "Используется в основных pace-метриках",
            "Include"
        },
        {
            "Start lap",
            2,
            "lap_num = 1",
            "Старт, трафик и первый поворот сильно искажают темп",
            "Exclude"
        },
        {
            "Small competitor benchmark sample",
            3,
            "LapSampleSize < 4",
            "Недостаточно представителей основных команд для корректного relative benchmark",
            "Exclude"
        },
        {
            "Extreme lap time",
            4,
            "lap_time_sec < 60 или lap_time_sec > RaceFieldMedianSec * 1.35",
            "Круг явно не похож на репрезентативный гоночный темп",
            "Exclude"
        },
        {
            "Field-wide spike",
            5,
            "FieldMedianLapSec / RaceFieldMedianSec > 1.10",
            "Похоже на Safety Car / VSC, дождь или другое общее замедление поля",
            "Exclude"
        },
        {
            "Driver rolling outlier / pit lap",
            6,
            "ABS(lap_time_sec - DriverRollingMedianSec) > 8",
            "Похоже на pit lap, ошибку, повреждение, трафик или другой индивидуальный выброс",
            "Exclude"
        }
    }
)
```

`DimLapQualityRule[LapQuality]` сортировать по `DimLapQualityRule[LapQualitySort]`.

### `DimLapViewMode`

Создать через `New table` в DAX:

```DAX
DimLapViewMode =
DATATABLE(
    "Lap View Mode", STRING,
    {
        {"Clean laps"},
        {"Raw laps"}
    }
)
```

Связи с fact-таблицей не создавать. Таблица нужна только для переключателя raw / clean на страницах `Race Pace Evolution` и `Race Phases Comparison`.

### Связи

В `Model view` создать связи:

| From | To | Cardinality | Cross filter |
|---|---|---|---|
| `DimRace[race_ID]` | `FactLapPace[race_ID]` | One-to-many | Single |
| `DimConstructor[constructor_ID]` | `FactLapPace[constructor_ID]` | One-to-many | Single |
| `DimDriver[driver_ID]` | `FactLapPace[driver_ID]` | One-to-many | Single |
| `DimLapQualityRule[LapQuality]` | `FactLapPace[LapQuality]` | One-to-many | Single |

Отключить загрузку (`Enable load`) для:

- `stg_lap_times`;
- `stg_results`;
- `stg_races`;
- `stg_drivers`;
- `stg_constructors`;
- `stg_race_distance`;
- `FactLapBase`;
- `LapBenchmark`;
- `FieldLapBenchmark`;
- `RaceFieldBenchmark`.

Сортировки:

- `DimRace[RaceLabel]` сортировать по `DimRace[RaceSort]`;
- `FactLapPace[RacePhase]` сортировать по `FactLapPace[PhaseSort]`.
- `DimLapQualityRule[LapQuality]` сортировать по `DimLapQualityRule[LapQualitySort]`.

## 9. DAX-меры

Создать отдельную таблицу `Measures` через `Enter data` с одной пустой колонкой или хранить меры в `FactLapPace`.

### 9.1. Базовые метрики и качество выборки

```DAX
Total Lap Count :=
COUNTROWS(FactLapPace)
```

```DAX
Clean Lap Count :=
CALCULATE(
    COUNTROWS(FactLapPace),
    FactLapPace[IsCleanLap] = TRUE()
)
```

```DAX
Excluded Lap Count :=
CALCULATE(
    COUNTROWS(FactLapPace),
    FactLapPace[IsCleanLap] = FALSE()
)
```

```DAX
Clean Lap Share :=
DIVIDE([Clean Lap Count], [Total Lap Count])
```

```DAX
Excluded Lap Share :=
DIVIDE([Excluded Lap Count], [Total Lap Count])
```

```DAX
Average Lap Time Sec :=
CALCULATE(
    AVERAGE(FactLapPace[lap_time_sec]),
    FactLapPace[IsCleanLap] = TRUE()
)
```

```DAX
Average Lap Time Raw Sec :=
AVERAGE(FactLapPace[lap_time_sec])
```

```DAX
Median Lap Time Sec :=
CALCULATE(
    MEDIAN(FactLapPace[lap_time_sec]),
    FactLapPace[IsCleanLap] = TRUE()
)
```

```DAX
Median Lap Time Raw Sec :=
MEDIAN(FactLapPace[lap_time_sec])
```

```DAX
Average Relative Pace Sec :=
CALCULATE(
    AVERAGE(FactLapPace[RelativePaceDeltaSec]),
    FactLapPace[IsCleanLap] = TRUE()
)
```

```DAX
Average Relative Pace Raw Sec :=
AVERAGE(FactLapPace[RelativePaceDeltaSec])
```

```DAX
Median Relative Pace Sec :=
CALCULATE(
    MEDIAN(FactLapPace[RelativePaceDeltaSec]),
    FactLapPace[IsCleanLap] = TRUE()
)
```

```DAX
Median Relative Pace Raw Sec :=
MEDIAN(FactLapPace[RelativePaceDeltaSec])
```

Форматировать `Clean Lap Share` и `Excluded Lap Share` как проценты. Основные аналитические страницы используют clean-меры, а raw-меры нужны для страницы `Data Quality & Methodology`.

```DAX
Median Relative Pace View Sec :=
SWITCH(
    SELECTEDVALUE(DimLapViewMode[Lap View Mode], "Clean laps"),
    "Raw laps", [Median Relative Pace Raw Sec],
    [Median Relative Pace Sec]
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
Observed Pace Drift Sec :=
VAR EarlyPace = [Early Race Pace Sec]
VAR LatePace = [Late Race Pace Sec]
RETURN
IF(
    NOT ISBLANK(EarlyPace) && NOT ISBLANK(LatePace),
    LatePace - EarlyPace
)
```

`Observed Pace Drift Sec` здесь считается по относительному темпу, а не по абсолютному времени круга. Это лучше для сравнения разных трасс: отрицательное значение означает, что команда стала быстрее относительно бенчмарка к концу гонки; положительное - что команда просела относительно соперников. Не интерпретировать эту меру как чистую деградацию шин.

```DAX
Early Race Pace Raw Sec :=
AVERAGEX(
    VALUES(DimRace[race_ID]),
    CALCULATE(
        [Median Relative Pace Raw Sec],
        FactLapPace[RacePhase] = "Early"
    )
)
```

```DAX
Late Race Pace Raw Sec :=
AVERAGEX(
    VALUES(DimRace[race_ID]),
    CALCULATE(
        [Median Relative Pace Raw Sec],
        FactLapPace[RacePhase] = "Late"
    )
)
```

```DAX
Observed Pace Drift Raw Sec :=
VAR EarlyPace = [Early Race Pace Raw Sec]
VAR LatePace = [Late Race Pace Raw Sec]
RETURN
IF(
    NOT ISBLANK(EarlyPace) && NOT ISBLANK(LatePace),
    LatePace - EarlyPace
)
```

```DAX
Observed Pace Drift Clean vs Raw Delta Sec :=
[Observed Pace Drift Sec] - [Observed Pace Drift Raw Sec]
```

```DAX
Late Race Advantage Sec :=
[Observed Pace Drift Sec]
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
Team Consistency Index Raw Sec :=
AVERAGEX(
    VALUES(DimRace[race_ID]),
    CALCULATE(
        STDEV.P(FactLapPace[RelativePaceDeltaSec])
    )
)
```

```DAX
Consistency Clean vs Raw Delta Sec :=
[Team Consistency Index Sec] - [Team Consistency Index Raw Sec]
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

```DAX
Rolling Relative Pace 5 Laps View Sec :=
VAR CurrentLap = MAX(FactLapPace[lap_num])
RETURN
AVERAGEX(
    FILTER(
        ALLSELECTED(FactLapPace[lap_num]),
        FactLapPace[lap_num] <= CurrentLap
            && FactLapPace[lap_num] > CurrentLap - 5
    ),
    [Median Relative Pace View Sec]
)
```

`Rolling Relative Pace 5 Laps View Sec` использовать там, где нужен переключатель `Clean laps / Raw laps`. Для executive-выводов использовать только clean-меры.

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
Observed Pace Drift Rank :=
RANKX(
    ALL(DimConstructor[constructor_name]),
    [Observed Pace Drift Sec],
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
McLaren Observed Pace Drift Sec :=
CALCULATE(
    [Observed Pace Drift Sec],
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
McLaren Clean Lap Share :=
CALCULATE(
    [Clean Lap Share],
    REMOVEFILTERS(DimConstructor),
    DimConstructor[constructor_name] = "McLaren"
)
```

```DAX
Hypothesis Status :=
VAR DriftRank =
    CALCULATE(
        [Observed Pace Drift Rank],
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
VAR CleanShare =
    CALCULATE(
        [Clean Lap Share],
        REMOVEFILTERS(DimConstructor),
        DimConstructor[constructor_name] = "McLaren"
    )
VAR Score =
    IF(DriftRank <= 2, 1, 0)
        + IF(ConsistencyRank <= 2, 1, 0)
        + IF(LateAdvantage < 0, 1, 0)
VAR BaseStatus =
    SWITCH(
        TRUE(),
        Score = 3, "Confirmed",
        Score = 2, "Partially Confirmed",
        "Rejected"
    )
RETURN
IF(
    BaseStatus = "Confirmed" && CleanShare < 0.70,
    "Partially Confirmed",
    BaseStatus
)
```

Логика статуса:

- `Confirmed`: McLaren входит в топ-2 по `Observed Pace Drift`, топ-2 по consistency, улучшает относительный темп в Late phase и имеет достаточную долю clean laps;
- `Partially Confirmed`: выполняются два условия из трех;
- `Rejected`: выполняется меньше двух условий;
- если clean lap share McLaren ниже 70%, статус не должен быть выше `Partially Confirmed`, потому что выборка слишком сильно зависит от очистки.

## 10. Страницы дашборда

### Page 1 - Executive Summary

Цель: сразу ответить, подтверждается ли гипотеза.

Фильтры страницы:

- `DimRace[year]`: 2022-2026;
- `DimConstructor[constructor_name]`: McLaren, Ferrari, Mercedes, Red Bull.

Не ставить page-level filter `FactLapPace[IsCleanLap] = True` на этой странице: clean-меры уже фильтруют очищенные круги, а `Clean Lap Share` должен видеть и clean, и excluded laps.

Рекомендуемый основной срез:

- для Miami-анализа: `DimRace[circuit_name] = Miami Grand Prix`;
- для расширенного контекста: `DimRace[CircuitGroup] = Miami / similar street`.

Визуалы:

1. Card: `McLaren Observed Pace Drift Sec`.
2. Card: `McLaren Consistency Index Sec`.
3. Card: `McLaren Late Race Pace Rank`.
4. Card: `McLaren Clean Lap Share`.
5. Card или multi-row card: `Hypothesis Status`.
6. Clustered bar chart:
   - Axis: `DimConstructor[constructor_name]`;
   - Values: `Observed Pace Drift Sec`;
   - Sort: ascending;
   - Interpretation: ниже лучше.
7. Clustered bar chart:
   - Axis: `DimConstructor[constructor_name]`;
   - Values: `Team Consistency Index Sec`;
   - Sort: ascending;
   - Interpretation: ниже стабильнее.
8. Маленькая table:
   - `constructor_name`;
   - `Observed Pace Drift Sec`;
   - `Team Consistency Index Sec`;
   - `Late Race Pace Rank`;
   - `Clean Lap Share`;
   - `Position Gain Late vs Early`.
9. Warning-блок:
   - "Analysis based on lap time data only; tyre, pit stop, weather, DRS and Safety Car data are not available."

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
- `DimLapViewMode[Lap View Mode]`: Clean laps / Raw laps.

Визуалы:

1. Line chart:
   - X-axis: `FactLapPace[lap_num]`;
   - Y-axis: `Rolling Relative Pace 5 Laps View Sec`;
   - Legend: `DimConstructor[constructor_name]`;
   - Tooltip: `Median Relative Pace View Sec`, `LapQuality`, `Clean Lap Count`, `RacePhase`.
2. Secondary line chart по пилотам McLaren:
   - X-axis: `lap_num`;
   - Y-axis: `Rolling Relative Pace 5 Laps View Sec`;
   - Legend: `DimDriver[driver_code]`;
   - Visual-level filter: `constructor_name = McLaren`.
3. Marker / scatter overlay для потенциально аномальных кругов:
   - X-axis: `lap_num`;
   - Y-axis: `RelativePaceDeltaSec`;
   - Legend: `LapQuality`;
   - Visual-level filter: `LapQuality` is not `Clean`.

Как читать:

- линия ниже нуля означает, что команда быстрее медианного бенчмарка топ-команд;
- если линия McLaren идет вниз к концу гонки, McLaren улучшает относительный темп;
- если линия McLaren растет вверх, темп ухудшается относительно соперников.

### Page 3 - Race Phases Comparison

Цель: сравнить Early / Mid / Late и проверить, меньше ли McLaren проседает к концу гонки.

Визуалы:

1. Clustered bar chart:
   - X-axis: `FactLapPace[RacePhase]`;
   - Values: `Median Relative Pace View Sec`;
   - Legend: `DimConstructor[constructor_name]`;
   - Sort `RacePhase` by `PhaseSort`.
2. Matrix:
   - Rows: `DimConstructor[constructor_name]`;
   - Columns: `FactLapPace[RacePhase]`;
   - Values: `Median Relative Pace View Sec`.
3. Slope-style line chart:
   - X-axis: `RacePhase`;
   - Y-axis: `Median Relative Pace View Sec`;
   - Legend: `constructor_name`.
4. Slicer:
   - `DimLapViewMode[Lap View Mode]`;
   - default: `Clean laps`.
5. Tooltip page для McLaren:
   - `DimDriver[driver_code]`;
   - `Median Relative Pace View Sec`;
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
   - Values: `Observed Pace Drift Sec`;
   - Visual-level filter: `constructor_name = McLaren`;
   - Sort: ascending.
3. Table:
   - `circuit_name`;
   - `RaceLabel`;
   - `Observed Pace Drift Sec`;
   - `Team Consistency Index Sec`;
   - `Late Race Pace Sec`;
   - `Clean Lap Count`;
   - `Clean Lap Share`;
   - filter: `constructor_name = McLaren`.
4. Small multiples bar chart:
   - Axis: `constructor_name`;
   - Values: `Observed Pace Drift Sec`;
   - Small multiples: `circuit_name`.

Как читать:

- нижний левый сектор scatter plot лучше: быстрый и стабильный относительный темп;
- если McLaren чаще находится ниже конкурентов по variability и observed pace drift на похожих трассах, гипотеза получает дополнительную поддержку.

### Page 5 - Data Quality & Methodology

Цель: показать ограничения анализа, правила очистки и устойчивость выводов после удаления потенциально аномальных кругов.

Фильтры страницы:

- `DimRace[year]`;
- `DimRace[circuit_name]`;
- `DimRace[RaceLabel]`;
- `DimConstructor[constructor_name]`.

Визуалы:

1. Cards:
   - `Total Lap Count`;
   - `Clean Lap Count`;
   - `Excluded Lap Count`;
   - `Clean Lap Share`;
   - `Excluded Lap Share`.
2. Stacked bar chart:
   - Axis: `DimConstructor[constructor_name]`;
   - Legend: `DimLapQualityRule[LapQuality]`;
   - Values: count of rows or `Total Lap Count`.
3. Matrix:
   - Rows: `DimRace[RaceLabel]`;
   - Columns: `DimLapQualityRule[LapQuality]`;
   - Values: count of rows.
4. Table с правилами очистки:
   - `DimLapQualityRule[LapQuality]`;
   - `DimLapQualityRule[CleaningRule]`;
   - `DimLapQualityRule[Interpretation]`;
   - `DimLapQualityRule[DefaultAction]`.
   - отдельно проверить строку `Start lap`, потому что это настройка "exclude first lap".
5. KPI comparison table:
   - `constructor_name`;
   - `Observed Pace Drift Raw Sec`;
   - `Observed Pace Drift Sec`;
   - `Observed Pace Drift Clean vs Raw Delta Sec`;
   - `Team Consistency Index Raw Sec`;
   - `Team Consistency Index Sec`;
   - `Consistency Clean vs Raw Delta Sec`.
6. Text / table block with missing factors:
   - tyres;
   - pit stops;
   - weather;
   - DRS;
   - Safety Car / VSC;
   - traffic and on-track battles.

Главный message страницы:

- очистка не доказывает причину аномалии, а только снижает риск искажения pace-метрик;
- если вывод по McLaren держится на clean laps и не переворачивается относительно raw laps, он надежнее;
- если clean lap share низкий или KPI сильно меняются после очистки, вывод нужно формулировать осторожно.

## 11. Финальные проверки перед презентацией

Проверить в Power BI:

1. В модель не загружены `driver_standings.csv` и `cons_standings.csv`.
2. В модель загружены только `FactLapPace`, `DimRace`, `DimConstructor`, `DimDriver`, `DimLapQualityRule`, `DimLapViewMode`.
3. Miami 2026 не попал в анализ, потому что это будущая целевая гонка.
4. В `FactLapPace` есть только команды McLaren, Ferrari, Mercedes, Red Bull.
5. `FieldLapBenchmark` и `RaceFieldBenchmark` рассчитаны до фильтрации `IsCoreCompetitor = true`, то есть по всему пелотону.
6. `DimLapViewMode` не связан с fact-таблицей и работает только как disconnected slicer.
7. `RacePhase` отсортирован как Early -> Mid -> Late.
8. `RaceLabel` отсортирован по `RaceSort`, а не по алфавиту.
9. Все основные executive-выводы используют clean-меры, а Page 5 показывает raw-vs-clean сравнение.
10. В Page 2 выбран один `RaceLabel` или один `circuit_name`, иначе линии по lap number будут смешивать разные гонки.
11. Отрицательный `RelativePaceDeltaSec` подписан как better/faster, чтобы зритель не перепутал направление метрики.
12. Карточка `Hypothesis Status` сверена вручную с графиками Page 1 и Page 3.
13. На всех страницах используется термин `Observed Pace Drift`, а не `Tyre Degradation`.
14. Page 5 показывает `Clean Lap Share`, причины исключения кругов и KPI до / после очистки.

## 12. Рекомендуемый короткий сценарий защиты

1. Page 1: показать статус гипотезы и два главных сравнения - `Observed Pace Drift` и `Consistency Index`.
2. Page 2: объяснить динамику по кругам: становится ли McLaren сильнее во второй половине гонки.
3. Page 3: показать Early / Mid / Late и связать изменение темпа с позициями.
4. Page 4: расширить вывод с Miami на похожие трассы и показать, является ли паттерн устойчивым.
5. Page 5: показать ограничения данных, долю очищенных кругов и сравнение KPI на raw / clean laps.

Финальная формулировка вывода должна зависеть от результата в Power BI:

- если McLaren имеет лучший или топ-2 `Observed Pace Drift`, низкий `Consistency Index`, отрицательный `Late Race Advantage` и достаточный `Clean Lap Share`, гипотеза подтверждается;
- если выполняются только два условия, гипотеза подтверждается частично;
- если McLaren не лучше конкурентов по drift и consistency, гипотеза отклоняется.

Финальный вывод формулировать как вывод о наблюдаемом темпе по очищенным lap-time данным. Не утверждать причинную связь с шинами, стратегией пит-стопов, DRS, погодой или Safety Car, если такие данные не добавлены в модель.
