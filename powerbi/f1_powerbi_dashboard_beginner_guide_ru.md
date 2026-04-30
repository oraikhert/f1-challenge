# Пошаговая инструкция по созданию Power BI дашборда Formula 1 Driver Pace Analysis

Эта инструкция помогает с нуля собрать Power BI дашборд по заданию из `f1_powerbi_task_statement_en.md`. Цель дашборда - проверить гипотезу: связаны ли отыгранные позиции от старта к финишу с улучшением относительного темпа пилота в поздней фазе гонки.

## 1. Что должно получиться

В конце у вас должен быть Power BI файл с 4 страницами:

1. `Executive Summary` - общий ответ на гипотезу.
2. `Race Phase Pace` - сравнение темпа по фазам гонки.
3. `Driver and Race Drilldown` - разбор конкретной гонки и пилота.
4. `Season and Constructor View` - проверка устойчивости эффекта по сезонам и командам.

Основная единица анализа: один пилот в одной гонке.

## 2. Какие данные использовать

Используйте CSV-файлы из папки `dataset`:

| Файл | Зачем нужен |
|---|---|
| `races.csv` | сезон, этап, дата гонки, название трассы |
| `results.csv` | стартовая позиция, финишная позиция, команда, статус |
| `lap_times.csv` | времена кругов и позиция пилота на каждом круге |
| `drivers.csv` | имя пилота |
| `constructors.csv` | команда/конструктор |

Файлы `driver_standings.csv` и `cons_standings.csv` для этого дашборда не обязательны.

## 3. Создайте новый Power BI файл

1. Откройте Power BI Desktop.
2. Нажмите `Get data` -> `Text/CSV`.
3. По очереди загрузите файлы:
   - `dataset/races.csv`;
   - `dataset/results.csv`;
   - `dataset/lap_times.csv`;
   - `dataset/drivers.csv`;
   - `dataset/constructors.csv`.
4. После выбора каждого файла нажимайте `Transform Data`, а не `Load`.
5. Когда все таблицы окажутся в Power Query, начните подготовку данных.

## 4. Подготовьте типы данных в Power Query

В Power Query проверьте типы столбцов.

### Таблица `races`

1. В столбцах `quali_date`, `quali_time`, `race_date`, `race_time` замените значение `\N` на `null`:
   - выберите столбец;
   - `Transform` -> `Replace Values`;
   - `Value To Find`: `\N`;
   - `Replace With`: оставьте пустым.
2. Для `race_date` выберите тип `Date`.
3. Если Power BI неправильно распознает дату, используйте:
   - правый клик по столбцу `race_date`;
   - `Change Type` -> `Using Locale`;
   - `Data Type`: `Date`;
   - `Locale`: `English (United Kingdom)`.
4. Типы:
   - `race_ID`, `year`, `round`, `circuit_ID` -> `Whole Number`;
   - `race_date` -> `Date`;
   - остальные текстовые поля -> `Text`.
5. Добавьте пользовательский столбец `Race Label`:

```powerquery
Text.From([year]) & " R" & Text.PadStart(Text.From([round]), 2, "0") & " - " & [circuit_name]
```

### Таблица `drivers`

1. Типы:
   - `driver_ID` -> `Whole Number`;
   - `driver_dob` -> `Date`;
   - остальные поля -> `Text`.
2. Добавьте пользовательский столбец `Driver Name`:

```powerquery
[driver_forename] & " " & [driver_surname]
```

### Таблица `constructors`

1. Типы:
   - `constructor_ID` -> `Whole Number`;
   - остальные поля -> `Text`.

### Таблица `results`

1. В текстовых столбцах замените `\N` на `null`, если такие значения есть.
2. Типы:
   - `result_ID`, `race_ID`, `driver_ID`, `constructor_ID` -> `Whole Number`;
   - `starting_position`, `race_position`, `points`, `total_laps`, `total_time_ms` -> числовой тип;
   - `status` -> `Text`.
3. Добавьте пользовательский столбец `DriverRaceKey`:

```powerquery
Text.From([race_ID]) & "-" & Text.From([driver_ID])
```

### Таблица `lap_times`

1. Типы:
   - `race_ID`, `driver_ID`, `lap_num`, `position`, `lap_time_ms` -> `Whole Number`;
   - `lap_time` -> `Text`.
2. Добавьте пользовательский столбец `DriverRaceKey`:

```powerquery
Text.From([race_ID]) & "-" & Text.From([driver_ID])
```

## 5. Создайте фазы гонки

Нужно разделить каждую гонку на 3 фазы:

| Фаза | Диапазон дистанции |
|---|---|
| `Initial` | 0-25% гонки |
| `Middle` | 40-60% гонки |
| `Late` | 75-100% гонки |

Первый круг исключаем из расчета темпа.

### 5.1. Создайте таблицу `RaceLapCount`

1. Правый клик по `lap_times`.
2. Выберите `Reference`.
3. Переименуйте новую таблицу в `RaceLapCount`.
4. Нажмите `Group By`.
5. Настройте:
   - `Group by`: `race_ID`;
   - `New column name`: `MaxRaceLap`;
   - `Operation`: `Max`;
   - `Column`: `lap_num`.

Эта таблица показывает, сколько кругов было в каждой гонке.

### 5.2. Создайте таблицу `lap_times_phase`

1. Правый клик по `lap_times`.
2. Выберите `Reference`.
3. Переименуйте новую таблицу в `lap_times_phase`.
4. Выполните `Merge Queries`:
   - первая таблица: `lap_times_phase`;
   - вторая таблица: `RaceLapCount`;
   - ключ: `race_ID`;
   - тип соединения: `Left Outer`.
5. Разверните присоединенную таблицу и оставьте только столбец `MaxRaceLap`.
6. Добавьте пользовательский столбец `Race Progress`:

```powerquery
[lap_num] / [MaxRaceLap]
```

7. Добавьте пользовательский столбец `RacePhase`:

```powerquery
if [lap_num] = 1 then null
else if [Race Progress] <= 0.25 then "Initial"
else if [Race Progress] >= 0.40 and [Race Progress] <= 0.60 then "Middle"
else if [Race Progress] >= 0.75 and [Race Progress] <= 1 then "Late"
else null
```

8. Отфильтруйте `RacePhase`: уберите `null`.
9. Отфильтруйте `lap_time_ms`: оставьте только значения больше 0.

## 6. Рассчитайте относительный темп по фазам

Относительный темп считается так:

```text
Relative Pace Phase % = Driver Avg Lap Time Phase / Field Median Lap Time Phase - 1
```

Важно: значение ниже 0 означает, что пилот быстрее медианы пелотона. Значение выше 0 означает, что пилот медленнее.

### 6.1. Создайте таблицу `FieldMedianRacePhase`

1. Правый клик по `lap_times_phase`.
2. Выберите `Reference`.
3. Переименуйте таблицу в `FieldMedianRacePhase`.
4. Откройте `Advanced Editor`.
5. Используйте такую логику группировки:

```powerquery
let
    Source = lap_times_phase,
    GroupedRows = Table.Group(
        Source,
        {"race_ID", "RacePhase"},
        {{"Field Median Lap Time ms", each List.Median([lap_time_ms]), type number}}
    )
in
    GroupedRows
```

Если Power BI просит подтвердить имя шага или таблицы, убедитесь, что исходная таблица действительно называется `lap_times_phase`.

### 6.2. Создайте таблицу `DriverRacePhasePace`

1. Правый клик по `lap_times_phase`.
2. Выберите `Reference`.
3. Переименуйте таблицу в `DriverRacePhasePace`.
4. Нажмите `Group By`.
5. Выберите `Advanced`.
6. Группируйте по полям:
   - `race_ID`;
   - `driver_ID`;
   - `DriverRaceKey`;
   - `RacePhase`.
7. Добавьте агрегаты:
   - `Driver Avg Lap Time ms` -> `Average` по `lap_time_ms`;
   - `Phase Lap Count` -> `Count Rows`.
8. Выполните `Merge Queries` с таблицей `FieldMedianRacePhase`:
   - ключи: `race_ID` и `RacePhase`;
   - тип соединения: `Left Outer`.
9. Разверните столбец `Field Median Lap Time ms`.
10. Добавьте пользовательский столбец `Relative Pace %`:

```powerquery
[Driver Avg Lap Time ms] / [Field Median Lap Time ms] - 1
```

11. Добавьте столбец `Phase Order`:

```powerquery
if [RacePhase] = "Initial" then 1
else if [RacePhase] = "Middle" then 2
else if [RacePhase] = "Late" then 3
else null
```

Эта таблица нужна для графика темпа по фазам.

## 7. Создайте основную таблицу `DriverRaceMetrics`

Эта таблица должна содержать одну строку на сочетание `гонка + пилот`.

1. Правый клик по `DriverRacePhasePace`.
2. Выберите `Reference`.
3. Переименуйте таблицу в `DriverRaceMetrics`.
4. Оставьте только столбцы:
   - `race_ID`;
   - `driver_ID`;
   - `DriverRaceKey`;
   - `RacePhase`;
   - `Relative Pace %`.
5. Выберите столбец `RacePhase`.
6. Нажмите `Transform` -> `Pivot Column`.
7. В `Values Column` выберите `Relative Pace %`.
8. В `Advanced Options` выберите `Don't Aggregate`, если доступно. Если Power BI требует агрегат, выберите `Average`.
9. Переименуйте получившиеся столбцы:
   - `Initial` -> `Relative Pace Initial %`;
   - `Middle` -> `Relative Pace Middle %`;
   - `Late` -> `Relative Pace Late %`.
10. Выполните `Merge Queries` с таблицей `results` по ключу `DriverRaceKey`.
11. Разверните из `results` только поля:
   - `constructor_ID`;
   - `starting_position`;
   - `race_position`;
   - `status`.
12. Переименуйте:
   - `starting_position` -> `Starting Position`;
   - `race_position` -> `Finish Position`.
13. Добавьте пользовательский столбец `Position Gain`:

```powerquery
[Starting Position] - [Finish Position]
```

14. Добавьте пользовательский столбец `Position Change Group`:

```powerquery
if [Position Gain] > 0 then "Gained Positions"
else if [Position Gain] = 0 then "No Change"
else "Lost Positions"
```

15. Добавьте пользовательский столбец `Late Pace Improvement`:

```powerquery
(([Relative Pace Initial %] + [Relative Pace Middle %]) / 2) - [Relative Pace Late %]
```

16. Отфильтруйте строки, где пустые значения есть в этих полях:
   - `Starting Position`;
   - `Finish Position`;
   - `Relative Pace Initial %`;
   - `Relative Pace Middle %`;
   - `Relative Pace Late %`;
   - `Late Pace Improvement`.

Положительный `Late Pace Improvement` означает, что в поздней фазе пилот стал быстрее относительно пелотона.

## 8. Оставьте только нужные таблицы для модели

В Power Query можно отключить загрузку вспомогательных таблиц:

1. Правый клик по таблице.
2. Уберите галочку `Enable Load`.

Рекомендуется загрузить в модель:

| Таблица | Загружать? |
|---|---|
| `races` | да |
| `drivers` | да |
| `constructors` | да |
| `lap_times` | да |
| `DriverRaceMetrics` | да |
| `DriverRacePhasePace` | да |
| `results` | можно не загружать |
| `RaceLapCount` | нет |
| `lap_times_phase` | нет |
| `FieldMedianRacePhase` | нет |

После этого нажмите `Close & Apply`.

## 9. Настройте связи в модели

Откройте вкладку `Model view` и создайте связи:

| Откуда | Куда | Тип |
|---|---|---|
| `races[race_ID]` | `DriverRaceMetrics[race_ID]` | one-to-many |
| `drivers[driver_ID]` | `DriverRaceMetrics[driver_ID]` | one-to-many |
| `constructors[constructor_ID]` | `DriverRaceMetrics[constructor_ID]` | one-to-many |
| `DriverRaceMetrics[DriverRaceKey]` | `DriverRacePhasePace[DriverRaceKey]` | one-to-many |
| `races[race_ID]` | `lap_times[race_ID]` | one-to-many |
| `drivers[driver_ID]` | `lap_times[driver_ID]` | one-to-many |

Направление фильтрации оставьте стандартным: от таблицы `one` к таблице `many`.

Если Power BI предлагает many-to-many связь, остановитесь и проверьте:

- нет ли дублей в справочниках `races`, `drivers`, `constructors`;
- точно ли `DriverRaceMetrics` содержит одну строку на один `DriverRaceKey`;
- правильно ли создан `DriverRaceKey`.

## 10. Создайте DAX-меры

Откройте таблицу `DriverRaceMetrics`, нажмите `New measure` и добавьте меры ниже.

### Базовые KPI

```DAX
Race Count =
DISTINCTCOUNT(DriverRaceMetrics[race_ID])
```

```DAX
Driver-Race Observations =
COUNTROWS(DriverRaceMetrics)
```

```DAX
Average Position Gain =
AVERAGE(DriverRaceMetrics[Position Gain])
```

```DAX
Median Position Gain =
MEDIAN(DriverRaceMetrics[Position Gain])
```

```DAX
Median Late Pace Improvement =
MEDIAN(DriverRaceMetrics[Late Pace Improvement])
```

```DAX
Median Relative Pace Initial % =
MEDIAN(DriverRaceMetrics[Relative Pace Initial %])
```

```DAX
Median Relative Pace Middle % =
MEDIAN(DriverRaceMetrics[Relative Pace Middle %])
```

```DAX
Median Relative Pace Late % =
MEDIAN(DriverRaceMetrics[Relative Pace Late %])
```

### Мера для графиков по фазам

Создайте эту меру в таблице `DriverRacePhasePace`:

```DAX
Median Relative Pace by Phase % =
MEDIAN(DriverRacePhasePace[Relative Pace %])
```

### Разница между группами

```DAX
Group Difference Late Improvement =
VAR Gained =
    CALCULATE(
        MEDIAN(DriverRaceMetrics[Late Pace Improvement]),
        DriverRaceMetrics[Position Change Group] = "Gained Positions"
    )
VAR NotGained =
    CALCULATE(
        MEDIAN(DriverRaceMetrics[Late Pace Improvement]),
        DriverRaceMetrics[Position Change Group] <> "Gained Positions"
    )
RETURN
    Gained - NotGained
```

Положительное значение означает, что группа пилотов, отыгравших позиции, сильнее улучшила поздний темп, чем остальные.

### Корреляция между `Position Gain` и `Late Pace Improvement`

```DAX
Correlation Position Gain vs Late Pace Improvement =
VAR T =
    FILTER(
        ADDCOLUMNS(
            SUMMARIZE(
                DriverRaceMetrics,
                DriverRaceMetrics[race_ID],
                DriverRaceMetrics[driver_ID]
            ),
            "X", CALCULATE(AVERAGE(DriverRaceMetrics[Position Gain])),
            "Y", CALCULATE(AVERAGE(DriverRaceMetrics[Late Pace Improvement]))
        ),
        NOT ISBLANK([X]) && NOT ISBLANK([Y])
    )
VAR AvgX = AVERAGEX(T, [X])
VAR AvgY = AVERAGEX(T, [Y])
VAR Numerator =
    SUMX(T, ([X] - AvgX) * ([Y] - AvgY))
VAR Denominator =
    SQRT(
        SUMX(T, POWER([X] - AvgX, 2))
            * SUMX(T, POWER([Y] - AvgY, 2))
    )
RETURN
    DIVIDE(Numerator, Denominator)
```

Интерпретация:

- значение больше 0: чем больше позиций отыграно, тем чаще лучше поздний темп;
- значение около 0: устойчивой связи не видно;
- значение меньше 0: больше отыгранных позиций не связано с улучшением позднего темпа.

### Направление связи

```DAX
Relationship Direction =
VAR Corr = [Correlation Position Gain vs Late Pace Improvement]
RETURN
    SWITCH(
        TRUE(),
        ISBLANK(Corr), "No data",
        Corr > 0, "Positive",
        Corr < 0, "Negative",
        "Flat"
    )
```

### Текстовый вердикт по гипотезе

```DAX
Hypothesis Verdict =
VAR Corr = [Correlation Position Gain vs Late Pace Improvement]
VAR Diff = [Group Difference Late Improvement]
RETURN
    SWITCH(
        TRUE(),
        ISBLANK(Corr) || ISBLANK(Diff), "Requires clarification",
        Corr >= 0.10 && Diff > 0, "Hypothesis supported",
        Corr <= -0.10 || Diff <= 0, "Hypothesis not supported",
        "Requires clarification"
    )
```

Порог `0.10` выбран как простой ориентир для учебного дашборда. Его можно изменить, если в проекте будет принято другое правило.

## 11. Настройте формат чисел

В `Model view` или `Data view` задайте формат `Percentage` для полей:

- `Relative Pace Initial %`;
- `Relative Pace Middle %`;
- `Relative Pace Late %`;
- `Late Pace Improvement`;
- `Relative Pace %`;
- `Median Late Pace Improvement`;
- `Median Relative Pace by Phase %`;
- `Group Difference Late Improvement`.

Рекомендуемое количество знаков после запятой: 2.

Для корреляции используйте формат `Decimal number`, 2 или 3 знака после запятой.

## 12. Страница 1: `Executive Summary`

Цель страницы: быстро ответить, подтверждается ли гипотеза в целом.

### 12.1. Добавьте slicer-фильтры

Добавьте slicers:

- `races[year]`;
- `races[Race Label]`;
- `drivers[Driver Name]`;
- `constructors[constructor_name]`.

Разместите их слева или сверху.

### 12.2. Добавьте KPI-карточки

Создайте карточки:

- `Race Count`;
- `Driver-Race Observations`;
- `Average Position Gain`;
- `Median Late Pace Improvement`;
- `Correlation Position Gain vs Late Pace Improvement`;
- `Hypothesis Verdict`.

### 12.3. Scatter plot

Добавьте `Scatter chart`:

- `X-axis`: `DriverRaceMetrics[Position Gain]`;
- `Y-axis`: `DriverRaceMetrics[Late Pace Improvement]`;
- `Details`: `DriverRaceMetrics[DriverRaceKey]`;
- `Legend`: `DriverRaceMetrics[Position Change Group]`;
- `Tooltips`:
  - `drivers[Driver Name]`;
  - `races[Race Label]`;
  - `constructors[constructor_name]`;
  - `DriverRaceMetrics[Starting Position]`;
  - `DriverRaceMetrics[Finish Position]`.

В настройках `Analytics` добавьте `Trend line`, если она доступна.

### 12.4. Bar chart по группам

Добавьте `Clustered bar chart`:

- `Y-axis`: `DriverRaceMetrics[Position Change Group]`;
- `X-axis`: `Median Late Pace Improvement`.

Задайте сортировку:

1. `Gained Positions`;
2. `No Change`;
3. `Lost Positions`.

Если порядок сортировки неудобно настроить вручную, это не критично для первого варианта дашборда.

### 12.5. Текстовый вывод

Добавьте текстовый блок с коротким объяснением:

```text
Положительный Late Pace Improvement означает улучшение позднего темпа относительно начальной и средней фаз. Гипотеза считается поддержанной, если корреляция положительная и группа Gained Positions имеет более высокий Late Pace Improvement, чем остальные.
```

## 13. Страница 2: `Race Phase Pace`

Цель страницы: показать, как меняется темп в группах `Gained Positions`, `No Change`, `Lost Positions`.

### 13.1. Line chart по фазам гонки

Добавьте `Line chart`:

- `X-axis`: `DriverRacePhasePace[RacePhase]`;
- `Y-axis`: `Median Relative Pace by Phase %`;
- `Legend`: `DriverRaceMetrics[Position Change Group]`.

Чтобы фазы шли в правильном порядке:

1. Выберите столбец `DriverRacePhasePace[RacePhase]`.
2. Нажмите `Sort by column`.
3. Выберите `DriverRacePhasePace[Phase Order]`.

Важно: на этом графике линия ниже 0 означает более быстрый темп.

### 13.2. Matrix или heatmap

Добавьте `Matrix`:

- `Rows`: `drivers[Driver Name]` или `constructors[constructor_name]`;
- `Columns`: `DriverRacePhasePace[RacePhase]`;
- `Values`: `Median Relative Pace by Phase %`.

Включите `Conditional formatting`:

- отрицательные значения выделяйте зеленым;
- положительные значения выделяйте красным.

### 13.3. Bar chart по улучшению позднего темпа

Добавьте `Clustered column chart`:

- `X-axis`: `DriverRaceMetrics[Position Change Group]`;
- `Y-axis`: `Median Late Pace Improvement`.

Добавьте slicers:

- `races[year]`;
- `races[Race Label]`;
- `constructors[constructor_name]`;
- `DriverRaceMetrics[status]`.

## 14. Страница 3: `Driver and Race Drilldown`

Цель страницы: проверить общий вывод на конкретной гонке и пилоте.

### 14.1. Фильтры страницы

Добавьте slicers:

- `races[year]`;
- `races[Race Label]`;
- `drivers[Driver Name]`;
- `constructors[constructor_name]`.

Для этой страницы удобно выбирать одну гонку и 1-3 пилотов.

### 14.2. Таблица пилотов в гонке

Добавьте `Table`:

- `drivers[Driver Name]`;
- `constructors[constructor_name]`;
- `DriverRaceMetrics[Starting Position]`;
- `DriverRaceMetrics[Finish Position]`;
- `DriverRaceMetrics[Position Gain]`;
- `DriverRaceMetrics[Position Change Group]`;
- `DriverRaceMetrics[Relative Pace Initial %]`;
- `DriverRaceMetrics[Relative Pace Middle %]`;
- `DriverRaceMetrics[Relative Pace Late %]`;
- `DriverRaceMetrics[Late Pace Improvement]`;
- `DriverRaceMetrics[status]`.

Отсортируйте таблицу по `Finish Position` по возрастанию.

### 14.3. График позиции по кругам

Добавьте `Line chart`:

- `X-axis`: `lap_times[lap_num]`;
- `Y-axis`: `Average of lap_times[position]`;
- `Legend`: `drivers[Driver Name]`.

В настройках оси Y включите обратный порядок, если доступно: позиция 1 должна быть наверху, а не внизу.

### 14.4. График времени круга

Добавьте меру в таблице `lap_times`:

```DAX
Selected Driver Lap Time ms =
AVERAGE(lap_times[lap_time_ms])
```

Добавьте еще одну меру:

```DAX
Field Median Lap Time ms =
CALCULATE(
    MEDIAN(lap_times[lap_time_ms]),
    REMOVEFILTERS(drivers)
)
```

Создайте `Line chart`:

- `X-axis`: `lap_times[lap_num]`;
- `Y-axis`:
  - `Selected Driver Lap Time ms`;
  - `Field Median Lap Time ms`.

Этот график показывает, когда выбранный пилот был быстрее или медленнее медианного темпа пелотона.

## 15. Страница 4: `Season and Constructor View`

Цель страницы: проверить, не создается ли эффект только отдельными гонками или командами.

### 15.1. Тренд корреляции по сезонам

Добавьте `Line chart`:

- `X-axis`: `races[year]`;
- `Y-axis`: `Correlation Position Gain vs Late Pace Improvement`.

Если линия сильно меняется от сезона к сезону, связь нестабильна.

### 15.2. Bar chart по конструкторам

Добавьте `Clustered bar chart`:

- `Y-axis`: `constructors[constructor_name]`;
- `X-axis`: `Median Late Pace Improvement`.

Отсортируйте по `Median Late Pace Improvement`.

### 15.3. Scatter plot по сезонам

Добавьте `Scatter chart`:

- `X-axis`: `Median Position Gain`;
- `Y-axis`: `Median Late Pace Improvement`;
- `Details`: `races[year]`.

Этот график помогает увидеть, какие сезоны выбиваются из общей картины.

### 15.4. Таблица сезонов

Добавьте `Table`:

- `races[year]`;
- `Race Count`;
- `Driver-Race Observations`;
- `Median Position Gain`;
- `Median Late Pace Improvement`;
- `Correlation Position Gain vs Late Pace Improvement`;
- `Relationship Direction`.

## 16. Финальная проверка дашборда

Перед сдачей проверьте 8 вещей.

1. В анализ попадают гонки с lap times, а не все гонки с 1950 года.
2. `race_ID` нигде не используется как признак хронологии. Для времени используйте `year`, `round`, `race_date`.
3. Первый круг исключен из расчета фазового темпа.
4. `Position Gain` считается как `Starting Position - Finish Position`.
5. Положительный `Position Gain` означает, что пилот отыграл позиции.
6. Отрицательный `Relative Pace %` означает, что пилот быстрее медианного темпа пелотона.
7. Положительный `Late Pace Improvement` означает улучшение позднего относительного темпа.
8. При выборе сезона, гонки, пилота или конструктора все графики пересчитываются.

## 17. Как сформулировать итоговый вывод

Если гипотеза поддерживается, используйте такой шаблон:

```text
В выбранном периоде пилоты, отыгравшие позиции от старта к финишу, в среднем показывают лучшее улучшение позднего относительного темпа. Корреляция между Position Gain и Late Pace Improvement положительная, а медианное Late Pace Improvement у группы Gained Positions выше, чем у остальных. Это поддерживает гипотезу, но не доказывает причинность, потому что в модели не учтены пит-стопы, шины, Safety Car, штрафы и гоночные инциденты.
```

Если гипотеза не поддерживается, используйте такой шаблон:

```text
В выбранном периоде не видно устойчивой положительной связи между отыгранными позициями и улучшением позднего относительного темпа. Корреляция слабая или отрицательная, либо группа Gained Positions не показывает более высокий Late Pace Improvement. Значит, изменение позиции, вероятно, чаще объясняется другими факторами: стратегией, пит-стопами, сходами соперников, штрафами или обстоятельствами конкретной гонки.
```

Если результат неоднозначный:

```text
Результат требует уточнения: на агрегированном уровне связь есть не во всех срезах или она нестабильна по сезонам, гонкам и конструкторам. Нужно дополнительно проверить отдельные гонки, выбросы, статусы финиша и возможное влияние факторов, которых нет в датасете.
```

## 18. Частые ошибки новичков

| Ошибка | Почему это проблема |
|---|---|
| Использовать `race_ID` как порядок гонок | `race_ID` технический идентификатор, он не отражает календарь |
| Не исключить первый круг | первый круг искажает темп из-за старта и борьбы |
| Перепутать знак `Relative Pace %` | меньше 0 означает быстрее, а не хуже |
| Перепутать формулу `Position Gain` | нужно `Starting Position - Finish Position`, а не наоборот |
| Считать средний темп по всем гонкам без фаз | гипотеза именно про изменение темпа по ходу гонки |
| Делать вывод только по scatter plot | нужно также смотреть группы, сезоны и конкретные гонки |
| Игнорировать статусы финиша | сходы, дисквалификации и технические проблемы могут искажать связь |

## 19. Рекомендуемое имя файла

Сохраните Power BI проект как:

```text
powerbi/F1_Driver_Pace_Analysis.pbix
```

Markdown-инструкцию можно держать рядом с `.pbix`, чтобы было понятно, как дашборд был собран.
