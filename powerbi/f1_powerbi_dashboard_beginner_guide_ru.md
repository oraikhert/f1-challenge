# Пошаговая инструкция по созданию Power BI дашборда Formula 1 Driver Pace Analysis

Эта инструкция помогает с нуля собрать Power BI дашборд по заданию из `f1_powerbi_task_statement_en.md`. Цель дашборда - проверить гипотезу: связаны ли отыгранные позиции от старта к финишу с улучшением относительного темпа пилота в поздней фазе гонки относительно средней фазы.

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

### Правило именования

Чтобы модель была предсказуемой, используйте единый стиль:

- исходные таблицы и столбцы оставляйте как в CSV: `lap_times`, `driver_ID`, `starting_position`;
- новые технические таблицы и столбцы называйте в `snake_case`: `driver_race_key`, `race_phase`, `late_vs_middle_pace_improvement`;
- значения категорий, которые видны в легендах и фильтрах, оставляйте человекочитаемыми: `Gained Positions`, `No Change`, `Lost Positions`;
- DAX-меры можно называть человекочитаемо: `Race Count`, `Median Late vs Middle Pace Improvement`;
- в визуалах можно переименовать поле только для конкретного графика через `Rename for this visual`, например показать `driver_name` как `Driver`.

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
5. Добавьте пользовательский столбец `race_label`:

```powerquery
Text.From([year]) & " R" & Text.PadStart(Text.From([round]), 2, "0") & " - " & [circuit_name]
```

### Таблица `drivers`

1. Типы:
   - `driver_ID` -> `Whole Number`;
   - `driver_dob` -> `Date`;
   - остальные поля -> `Text`.
2. Добавьте пользовательский столбец `driver_name`:

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
3. Добавьте пользовательский столбец `starting_position_clean`:

```powerquery
if [starting_position] = 0 then null else [starting_position]
```

В этом датасете `starting_position = 0` не является реальной стартовой позицией. Это специальный код для случаев без обычного места на стартовой решетке: например, не прошел квалификацию, снялся, стартовал нестандартно или имеет другой особый статус. Оригинальное поле `starting_position` оставляем для аудита данных, а в расчетах используем `starting_position_clean`.

4. Добавьте пользовательский столбец `driver_race_key`:

```powerquery
Text.From([race_ID]) & "-" & Text.From([driver_ID])
```

### Таблица `lap_times`

1. Типы:
   - `race_ID`, `driver_ID`, `lap_num`, `position`, `lap_time_ms` -> `Whole Number`;
   - `lap_time` -> `Text`.
2. Добавьте пользовательский столбец `driver_race_key`:

```powerquery
Text.From([race_ID]) & "-" & Text.From([driver_ID])
```

## 5. Создайте фазы гонки

Нужно разделить каждую гонку на 3 фазы:

| Фаза | Диапазон дистанции |
|---|---|
| `initial` | 0-25% гонки |
| `middle` | 40-60% гонки |
| `late` | 75-100% гонки |

Первый круг исключаем из расчета темпа.

### 5.1. Создайте таблицу `race_lap_count`

1. Правый клик по `lap_times`.
2. Выберите `Reference`.
3. Переименуйте новую таблицу в `race_lap_count`.
4. Нажмите `Group By`.
5. Настройте:
   - `Group by`: `race_ID`;
   - `New column name`: `max_race_lap`;
   - `Operation`: `Max`;
   - `Column`: `lap_num`.

Эта таблица показывает, сколько кругов было в каждой гонке.

### 5.2. Создайте таблицу `lap_times_phase`

1. Правый клик по `lap_times`.
2. Выберите `Reference`.
3. Переименуйте новую таблицу в `lap_times_phase`.
4. Выполните `Merge Queries`:
   - первая таблица: `lap_times_phase`;
   - вторая таблица: `race_lap_count`;
   - ключ: `race_ID`;
   - тип соединения: `Left Outer`.
5. Разверните присоединенную таблицу и оставьте только столбец `max_race_lap`.
6. Добавьте пользовательский столбец `race_progress`:

```powerquery
[lap_num] / [max_race_lap]
```

7. Добавьте пользовательский столбец `race_phase`:

```powerquery
if [lap_num] = 1 then null
else if [race_progress] <= 0.25 then "initial"
else if [race_progress] >= 0.40 and [race_progress] <= 0.60 then "middle"
else if [race_progress] >= 0.75 and [race_progress] <= 1 then "late"
else null
```

8. Отфильтруйте `race_phase`: уберите `null`.
9. Отфильтруйте `lap_time_ms`: оставьте только значения больше 0.

## 6. Рассчитайте относительный темп по фазам

Относительный темп считается так:

```text
Relative Pace Phase % = Driver Median Lap Time Phase / Peloton Median Lap Time Phase - 1
```

Важно: значение ниже 0 означает, что пилот быстрее медианы пелотона. Значение выше 0 означает, что пилот медленнее.

### 6.1. Создайте таблицу `peloton_median_race_phase`

1. Правый клик по `lap_times_phase`.
2. Выберите `Reference`.
3. Переименуйте таблицу в `peloton_median_race_phase`.
4. Откройте `Advanced Editor`.
5. Используйте такую логику группировки:

```powerquery
let
    Source = lap_times_phase,
    grouped_rows = Table.Group(
        Source,
        {"race_ID", "race_phase"},
        {{"peloton_median_lap_time_ms", each List.Median([lap_time_ms]), type number}}
    )
in
    grouped_rows
```

Если Power BI просит подтвердить имя шага или таблицы, убедитесь, что исходная таблица действительно называется `lap_times_phase`.

### 6.2. Создайте таблицу `driver_race_phase_pace`

1. Правый клик по `lap_times_phase`.
2. Выберите `Reference`.
3. Переименуйте таблицу в `driver_race_phase_pace`.
4. Нажмите `Group By`.
5. Выберите `Advanced`.
6. Группируйте по полям:
   - `race_ID`;
   - `driver_ID`;
   - `driver_race_key`;
   - `race_phase`.
7. Добавьте агрегаты:
   - `driver_median_lap_time_ms` -> `Median` по `lap_time_ms`;
   - `phase_lap_count` -> `Count Rows`.

Если в вашем Power BI в `Group By` нет операции `Median`, откройте `Advanced Editor` для таблицы `driver_race_phase_pace` и используйте такую группировку:

```powerquery
let
    Source = lap_times_phase,
    grouped_rows = Table.Group(
        Source,
        {"race_ID", "driver_ID", "driver_race_key", "race_phase"},
        {
            {"driver_median_lap_time_ms", each List.Median([lap_time_ms]), type number},
            {"phase_lap_count", each Table.RowCount(_), Int64.Type}
        }
    )
in
    grouped_rows
```

Медиана по пилоту лучше защищает расчет от отдельных очень медленных кругов: пит-стопов, трафика, ошибок, повреждений или кругов с аномально высоким временем.

8. Выполните `Merge Queries` с таблицей `peloton_median_race_phase`:
   - ключи: `race_ID` и `race_phase`;
   - тип соединения: `Left Outer`.
9. Разверните столбец `peloton_median_lap_time_ms`.
10. Добавьте пользовательский столбец `relative_pace_pct`:

```powerquery
[driver_median_lap_time_ms] / [peloton_median_lap_time_ms] - 1
```

11. Добавьте столбец `phase_order`:

```powerquery
if [race_phase] = "initial" then 1
else if [race_phase] = "middle" then 2
else if [race_phase] = "late" then 3
else null
```

Эта таблица нужна для графика темпа по фазам.

## 7. Создайте основную таблицу `driver_race_metrics`

Эта таблица должна содержать одну строку на сочетание `гонка + пилот`.

1. Правый клик по `driver_race_phase_pace`.
2. Выберите `Reference`.
3. Переименуйте таблицу в `driver_race_metrics`.
4. Оставьте только столбцы:
   - `race_ID`;
   - `driver_ID`;
   - `driver_race_key`;
   - `race_phase`;
   - `relative_pace_pct`.
5. Выберите столбец `race_phase`.
6. Нажмите `Transform` -> `Pivot Column`.
7. В `Values Column` выберите `relative_pace_pct`.
8. В `Advanced Options` выберите `Don't Aggregate`, если доступно. Если Power BI требует агрегат, выберите `Average`: на этом этапе на одну гонку, одного пилота и одну фазу уже должна быть только одна строка, поэтому фактического усреднения кругов здесь не происходит.
9. Переименуйте получившиеся столбцы:
   - `initial` -> `relative_pace_initial_pct`;
   - `middle` -> `relative_pace_middle_pct`;
   - `late` -> `relative_pace_late_pct`.
10. Выполните `Merge Queries` с таблицей `results` по ключу `driver_race_key`.
11. Разверните из `results` только поля:
   - `constructor_ID`;
   - `starting_position_clean`;
   - `race_position`;
   - `status`.
12. Переименуйте:
   - `race_position` -> `finish_position`.
13. Добавьте пользовательский столбец `position_gain`:

```powerquery
[starting_position_clean] - [finish_position]
```

Здесь используется очищенная стартовая позиция: все исходные `starting_position = 0` превращены в `null`, чтобы не считать ложную потерю позиций.

14. Добавьте пользовательский столбец `position_change_group`:

```powerquery
if [position_gain] > 0 then "Gained Positions"
else if [position_gain] = 0 then "No Change"
else "Lost Positions"
```

15. Добавьте пользовательский столбец `late_vs_middle_pace_improvement`:

```powerquery
[relative_pace_middle_pct] - [relative_pace_late_pct]
```

Это основная метрика для проверки гипотезы. Положительное значение означает, что в поздней фазе пилот стал быстрее относительно пелотона, чем был в средней фазе.

16. Добавьте пользовательский столбец `late_vs_initial_pace_improvement`:

```powerquery
[relative_pace_initial_pct] - [relative_pace_late_pct]
```

Это справочная метрика. Она показывает улучшение позднего относительного темпа относительно начальной фазы, но не используется в основном вердикте.

17. Добавьте пользовательский столбец `late_pace_improvement`:

```powerquery
(([relative_pace_initial_pct] + [relative_pace_middle_pct]) / 2) - [relative_pace_late_pct]
```

Это старая summary-метрика. Она сохраняется для сравнения и истории, но не используется в основном `Hypothesis Verdict`. Здесь деление на 2 означает среднее двух уже рассчитанных фазовых значений `relative_pace_initial_pct` и `relative_pace_middle_pct`; это не среднее время круга.

18. Отфильтруйте строки, где пустые значения есть в этих полях:
   - `starting_position_clean`;
   - `finish_position`;
   - `relative_pace_initial_pct`;
   - `relative_pace_middle_pct`;
   - `relative_pace_late_pct`;
   - `late_vs_middle_pace_improvement`;
   - `late_vs_initial_pace_improvement`;
   - `late_pace_improvement`.

Положительный `late_vs_middle_pace_improvement` означает, что в поздней фазе пилот стал быстрее относительно пелотона, чем был в средней фазе.

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
| `driver_race_metrics` | да |
| `driver_race_phase_pace` | да |
| `results` | можно не загружать |
| `race_lap_count` | нет |
| `lap_times_phase` | нет |
| `peloton_median_race_phase` | нет |

После этого нажмите `Close & Apply`.

## 9. Настройте связи в модели

Откройте вкладку `Model view` и создайте связи:

| Откуда | Куда | Тип |
|---|---|---|
| `races[race_ID]` | `driver_race_metrics[race_ID]` | one-to-many |
| `drivers[driver_ID]` | `driver_race_metrics[driver_ID]` | one-to-many |
| `constructors[constructor_ID]` | `driver_race_metrics[constructor_ID]` | one-to-many |
| `driver_race_metrics[driver_race_key]` | `driver_race_phase_pace[driver_race_key]` | one-to-many |
| `races[race_ID]` | `lap_times[race_ID]` | one-to-many |
| `drivers[driver_ID]` | `lap_times[driver_ID]` | one-to-many |

Направление фильтрации оставьте стандартным: от таблицы `one` к таблице `many`.

Если Power BI предлагает many-to-many связь, остановитесь и проверьте:

- нет ли дублей в справочниках `races`, `drivers`, `constructors`;
- точно ли `driver_race_metrics` содержит одну строку на один `driver_race_key`;
- правильно ли создан `driver_race_key`.

## 10. Создайте DAX-меры

Ниже указано, в какой таблице создавать каждую меру. Чтобы создать меру, выберите нужную таблицу в панели `Data`, нажмите `New measure` и вставьте DAX-код.

В Power BI мера технически может лежать почти в любой таблице, но для порядка храните ее рядом с таблицей, на которой она в основном считается:

| Мера | Где создать |
|---|---|
| `Race Count` | `driver_race_metrics` |
| `Driver-Race Observations` | `driver_race_metrics` |
| `Average Position Gain` | `driver_race_metrics` |
| `Median Position Gain` | `driver_race_metrics` |
| `Median Late vs Middle Pace Improvement` | `driver_race_metrics` |
| `Gained Median Late vs Middle Pace Improvement` | `driver_race_metrics` |
| `Median Late vs Initial Pace Improvement` | `driver_race_metrics`, справочная мера |
| `Median Late Pace Improvement` | `driver_race_metrics` |
| `Median Relative Pace Initial %` | `driver_race_metrics` |
| `Median Relative Pace Middle %` | `driver_race_metrics` |
| `Median Relative Pace Late %` | `driver_race_metrics` |
| `Spearman Correlation Position Gain vs Late vs Middle Pace Improvement` | `driver_race_metrics` |
| `Pearson Correlation Position Gain vs Late vs Middle Pace Improvement` | `driver_race_metrics`, справочная мера |
| `Group Difference Late Improvement` | `driver_race_metrics`, справочная мера |
| `Relationship Direction` | `driver_race_metrics` |
| `Hypothesis Verdict` | `driver_race_metrics` |
| `Median Relative Pace by Phase %` | `driver_race_phase_pace` |
| `Selected Driver Median Lap Time ms` | `lap_times` |
| `Peloton Median Lap Time ms` | `lap_times` |

### Базовые KPI

Создайте эти меры в таблице `driver_race_metrics`.

```DAX
Race Count =
DISTINCTCOUNT(driver_race_metrics[race_ID])
```

```DAX
Driver-Race Observations =
COUNTROWS(driver_race_metrics)
```

```DAX
Average Position Gain =
AVERAGE(driver_race_metrics[position_gain])
```

```DAX
Median Position Gain =
MEDIAN(driver_race_metrics[position_gain])
```

```DAX
Median Late vs Middle Pace Improvement =
MEDIAN(driver_race_metrics[late_vs_middle_pace_improvement])
```

```DAX
Gained Median Late vs Middle Pace Improvement =
CALCULATE(
    MEDIAN(driver_race_metrics[late_vs_middle_pace_improvement]),
    driver_race_metrics[position_change_group] = "Gained Positions"
)
```

Эта мера показывает медианное улучшение позднего относительного темпа относительно средней фазы только у пилотов, которые улучшили финишную позицию относительно стартовой. Для гипотезы это главный прямой тест: если значение больше 0, значит типичный пилот из группы `Gained Positions` в поздней фазе ехал лучше относительно пелотона, чем в средней фазе.

```DAX
Median Late vs Initial Pace Improvement =
MEDIAN(driver_race_metrics[late_vs_initial_pace_improvement])
```

Эта справочная мера показывает улучшение позднего относительного темпа относительно начальной фазы. Она помогает понять, насколько вывод зависит от шумной стартовой части гонки, но не используется в основном вердикте.

```DAX
Median Late Pace Improvement =
MEDIAN(driver_race_metrics[late_pace_improvement])
```

`Median Late Pace Improvement` оставляем как старую summary-метрику для сравнения. В основном `Hypothesis Verdict` она не используется.

```DAX
Median Relative Pace Initial % =
MEDIAN(driver_race_metrics[relative_pace_initial_pct])
```

```DAX
Median Relative Pace Middle % =
MEDIAN(driver_race_metrics[relative_pace_middle_pct])
```

```DAX
Median Relative Pace Late % =
MEDIAN(driver_race_metrics[relative_pace_late_pct])
```

### Мера для графиков по фазам

Создайте эту меру в таблице `driver_race_phase_pace`:

```DAX
Median Relative Pace by Phase % =
MEDIAN(driver_race_phase_pace[relative_pace_pct])
```

### Разница между группами

Создайте эту меру в таблице `driver_race_metrics`, если хотите сохранить старую проверку для истории и дополнительных комментариев. В новом основном вердикте и на странице `Executive Summary` эта мера не используется.

```DAX
Group Difference Late Improvement =
VAR Gained =
    CALCULATE(
        MEDIAN(driver_race_metrics[late_pace_improvement]),
        driver_race_metrics[position_change_group] = "Gained Positions"
    )
VAR NotGained =
    CALCULATE(
        MEDIAN(driver_race_metrics[late_pace_improvement]),
        driver_race_metrics[position_change_group] <> "Gained Positions"
    )
RETURN
    Gained - NotGained
```

Положительное значение означает, что группа пилотов, отыгравших позиции, сильнее улучшила поздний темп по старой summary-метрике, чем остальные. Это полезная справочная метрика, но она отвечает на более широкий вопрос сравнения групп и не участвует в новом основном вердикте. Для основного дашборда используем `Gained Median Late vs Middle Pace Improvement` и `Spearman Correlation Position Gain vs Late vs Middle Pace Improvement`.

### Spearman-корреляция между `position_gain` и `late_vs_middle_pace_improvement`

Создайте эту меру в таблице `driver_race_metrics`.

```DAX
Spearman Correlation Position Gain vs Late vs Middle Pace Improvement =
VAR T =
    FILTER(
        ADDCOLUMNS(
            SUMMARIZE(
                driver_race_metrics,
                driver_race_metrics[race_ID],
                driver_race_metrics[driver_ID]
            ),
            "X", CALCULATE(AVERAGE(driver_race_metrics[position_gain])),
            "Y", CALCULATE(AVERAGE(driver_race_metrics[late_vs_middle_pace_improvement]))
        ),
        NOT ISBLANK([X]) && NOT ISBLANK([Y])
    )
VAR RankedT =
    ADDCOLUMNS(
        T,
        "RankX",
            VAR CurrentX = [X]
            VAR LessCount =
                COUNTROWS(
                    FILTER(T, [X] < CurrentX)
                )
            VAR EqualCount =
                COUNTROWS(
                    FILTER(T, [X] = CurrentX)
                )
            RETURN
                LessCount + DIVIDE(EqualCount + 1, 2),
        "RankY",
            VAR CurrentY = [Y]
            VAR LessCount =
                COUNTROWS(
                    FILTER(T, [Y] < CurrentY)
                )
            VAR EqualCount =
                COUNTROWS(
                    FILTER(T, [Y] = CurrentY)
                )
            RETURN
                LessCount + DIVIDE(EqualCount + 1, 2)
    )
VAR AvgRankX = AVERAGEX(RankedT, [RankX])
VAR AvgRankY = AVERAGEX(RankedT, [RankY])
VAR Numerator =
    SUMX(RankedT, ([RankX] - AvgRankX) * ([RankY] - AvgRankY))
VAR Denominator =
    SQRT(
        SUMX(RankedT, POWER([RankX] - AvgRankX, 2))
            * SUMX(RankedT, POWER([RankY] - AvgRankY, 2))
    )
RETURN
    DIVIDE(Numerator, Denominator)
```

Spearman-корреляция смотрит не на сами значения, а на их порядок. Она отвечает на вопрос: если пилоты выше по `position_gain`, находятся ли они обычно выше и по `late_vs_middle_pace_improvement`. Это лучше подходит для текущей задачи, потому что данные Формулы 1 содержат выбросы: технические проблемы, аварии, очень медленные круги, пит-стопы и другие гоночные обстоятельства.

Интерпретация:

- значение больше 0: чем больше позиций отыграно, тем чаще лучше поздний относительный темп;
- значение около 0: устойчивого направления связи не видно;
- значение меньше 0: больше отыгранных позиций не связано с улучшением позднего относительного темпа.

### Pearson-корреляция между `position_gain` и `late_vs_middle_pace_improvement`

Создайте эту меру в таблице `driver_race_metrics`, если хотите сохранить старый расчет для сравнения. В новом основном вердикте она не используется.

```DAX
Pearson Correlation Position Gain vs Late vs Middle Pace Improvement =
VAR T =
    FILTER(
        ADDCOLUMNS(
            SUMMARIZE(
                driver_race_metrics,
                driver_race_metrics[race_ID],
                driver_race_metrics[driver_ID]
            ),
            "X", CALCULATE(AVERAGE(driver_race_metrics[position_gain])),
            "Y", CALCULATE(AVERAGE(driver_race_metrics[late_vs_middle_pace_improvement]))
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

Pearson-корреляция измеряет линейную связь по исходным числам. Она полезна как справочная метрика, но чувствительнее к выбросам, поэтому для основного ответа на гипотезу используем Spearman-корреляцию.

### Направление связи

Создайте эту меру в таблице `driver_race_metrics`.

```DAX
Relationship Direction =
VAR Corr = [Spearman Correlation Position Gain vs Late vs Middle Pace Improvement]
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

Создайте эту меру в таблице `driver_race_metrics`.

```DAX
Hypothesis Verdict =
VAR Spearman = [Spearman Correlation Position Gain vs Late vs Middle Pace Improvement]
VAR GainedMedian = [Gained Median Late vs Middle Pace Improvement]
RETURN
    SWITCH(
        TRUE(),
        ISBLANK(Spearman) || ISBLANK(GainedMedian), "Requires clarification",
        Spearman >= 0.10 && GainedMedian > 0, "Hypothesis supported",
        Spearman <= -0.10 || GainedMedian <= 0, "Hypothesis not supported",
        "Requires clarification"
    )
```

Новый вердикт использует два критерия:

- `Gained Median Late vs Middle Pace Improvement > 0`: пилоты, отыгравшие позиции, в поздней фазе действительно лучше относительно пелотона, чем в средней фазе;
- `Spearman Correlation >= 0.10`: в выбранном срезе есть положительное направление связи между величиной отыгрыша позиций и улучшением позднего относительного темпа относительно средней фазы.

Порог `0.10` выбран как простой ориентир для учебного дашборда, чтобы не считать микроскопическую положительную связь подтверждением гипотезы. Его можно изменить, если в проекте будет принято другое правило.

### Меры для графика времени круга

Создайте эти меры в таблице `lap_times`.

```DAX
Selected Driver Median Lap Time ms =
MEDIAN(lap_times[lap_time_ms])
```

```DAX
Peloton Median Lap Time ms =
CALCULATE(
    MEDIAN(lap_times[lap_time_ms]),
    REMOVEFILTERS(drivers)
)
```

Эти меры нужны для страницы `Driver and Race Drilldown`: первая показывает медианное время круга выбранного пилота, а вторая показывает медианное время круга пелотона на том же круге. Если выбран один пилот и одна гонка, медиана выбранного пилота равна его фактическому времени на конкретном круге.

### Дополнительные столбцы для tooltip scatter plot

Создайте эти calculated columns в таблице `driver_race_metrics`:

```DAX
Driver =
RELATED(drivers[driver_name])
```

```DAX
Race =
RELATED(races[race_label])
```

```DAX
Constructor =
RELATED(constructors[constructor_name])
```

Эти столбцы нужны для tooltip на scatter plot. Точка на scatter plot строится на уровне строки из `driver_race_metrics`, поэтому в tooltip безопаснее использовать текстовые поля из этой же таблицы. Если добавить в tooltip напрямую `drivers[driver_name]`, `races[race_label]` или `constructors[constructor_name]`, Power BI может показать неверное значение вроде `First driver_name`, потому что фильтр от точки scatter plot не обязан возвращаться обратно в справочник при направлении связи `Single`.

## 11. Настройте формат чисел

В `Model view` или `Data view` задайте формат `Percentage` для полей:

- `relative_pace_initial_pct`;
- `relative_pace_middle_pct`;
- `relative_pace_late_pct`;
- `late_vs_middle_pace_improvement`;
- `late_vs_initial_pace_improvement`;
- `late_pace_improvement`;
- `relative_pace_pct`;
- `Median Late vs Middle Pace Improvement`;
- `Gained Median Late vs Middle Pace Improvement`;
- `Median Late vs Initial Pace Improvement`;
- `Median Late Pace Improvement`;
- `Median Relative Pace by Phase %`;
- `Group Difference Late Improvement`.

Рекомендуемое количество знаков после запятой: 2.

Для Spearman- и Pearson-корреляции используйте формат `Decimal number`, 2 или 3 знака после запятой.

Перед сборкой страниц помните: в списке полей оставляем технические имена `snake_case`, а в конкретном визуале можно задать понятную подпись через правый клик по полю -> `Rename for this visual`. Например, `driver_race_metrics[position_gain]` можно показать как `Position Gain`, а `driver_race_metrics[late_vs_middle_pace_improvement]` как `Late vs Middle Pace Improvement`.

## 12. Страница 1: `Executive Summary`

Цель страницы: быстро ответить, подтверждается ли гипотеза в целом.

### 12.1. Добавьте slicer-фильтры

Добавьте slicers:

- `races[year]`;
- `races[race_label]`;
- `drivers[driver_name]`;
- `constructors[constructor_name]`.

Разместите их слева или сверху.

### 12.2. Добавьте KPI-карточки

Создайте карточки:

- `Race Count`;
- `Driver-Race Observations`;
- `Average Position Gain`;
- `Median Late vs Middle Pace Improvement`;
- `Gained Median Late vs Middle Pace Improvement`;
- `Spearman Correlation Position Gain vs Late vs Middle Pace Improvement`;
- `Hypothesis Verdict`.

### 12.3. Scatter plot

Добавьте `Scatter chart`:

- `Values`: `driver_race_metrics[driver_race_key]`;
- `X-axis`: `driver_race_metrics[position_gain]`, summarization `Average`;
- `Y-axis`: `driver_race_metrics[late_vs_middle_pace_improvement]`, summarization `Average`;
- `Legend`: `driver_race_metrics[position_change_group]`;
- `Tooltips`:
  - `driver_race_metrics[Driver]`;
  - `driver_race_metrics[Race]`;
  - `driver_race_metrics[Constructor]`;
  - `driver_race_metrics[starting_position_clean]`;
  - `driver_race_metrics[finish_position]`.

В некоторых версиях Power BI поле для детализации scatter chart называется `Values`, а не `Details`. После добавления `driver_race_key` в `Values` Power BI может попросить агрегировать оси X и Y. Выберите `Average` для обеих осей. Это корректно, потому что в `driver_race_metrics` один `driver_race_key` должен соответствовать одной строке, значит среднее по этой строке равно исходному значению.

Не включайте `Both` для связей только ради tooltip. Для этой модели нормальное направление фильтрации - `Single`; текстовые поля для tooltip решаются через calculated columns выше.

В настройках `Analytics` добавьте `Trend line`, если она доступна.

### 12.4. Bar chart по группам

Добавьте `Clustered bar chart`:

- `Y-axis`: `driver_race_metrics[position_change_group]`;
- `X-axis`: `Median Late vs Middle Pace Improvement`.

Задайте сортировку:

1. `Gained Positions`;
2. `No Change`;
3. `Lost Positions`.

Этот график показывает медианный `late_vs_middle_pace_improvement` по группам изменения позиции. Для нового вердикта особенно важна строка `Gained Positions`: ее значение соответствует смыслу меры `Gained Median Late vs Middle Pace Improvement`, которая участвует в `Hypothesis Verdict`.

Меру `Group Difference Late Improvement` оставляем в модели только как справочную историческую проверку. На страницу `Executive Summary` ее отдельной карточкой не добавляем и в `Hypothesis Verdict` не используем.

### 12.5. Текстовый вывод

Добавьте текстовый блок с коротким объяснением:

```text
Положительный late_vs_middle_pace_improvement означает, что поздний относительный темп лучше относительного темпа средней фазы. Гипотеза считается поддержанной, если у группы Gained Positions медианный late_vs_middle_pace_improvement больше 0, а Spearman-корреляция между position_gain и late_vs_middle_pace_improvement положительная и не ниже выбранного порога.
```

## 13. Страница 2: `Race Phase Pace`

Цель страницы: показать, как меняется темп в группах `Gained Positions`, `No Change`, `Lost Positions`.

### 13.1. Line chart по фазам гонки

Добавьте `Line chart`:

- `X-axis`: `driver_race_phase_pace[race_phase]`;
- `Y-axis`: `Median Relative Pace by Phase %`;
- `Legend`: `driver_race_metrics[position_change_group]`.

Чтобы фазы шли в правильном порядке:

1. Выберите столбец `driver_race_phase_pace[race_phase]`.
2. Нажмите `Sort by column`.
3. Выберите `driver_race_phase_pace[phase_order]`.

Важно: на этом графике линия ниже 0 означает более быстрый темп.

### 13.2. Matrix или heatmap

Добавьте `Matrix`:

- `Rows`: `drivers[driver_name]` или `constructors[constructor_name]`;
- `Columns`: `driver_race_phase_pace[race_phase]`;
- `Values`: `Median Relative Pace by Phase %`.

Включите `Conditional formatting`:

- отрицательные значения выделяйте зеленым;
- положительные значения выделяйте красным.

### 13.3. Bar chart по улучшению позднего темпа

Добавьте `Clustered column chart`:

- `X-axis`: `driver_race_metrics[position_change_group]`;
- `Y-axis`: `Median Late vs Middle Pace Improvement`.

Добавьте slicers:

- `races[year]`;
- `races[race_label]`;
- `constructors[constructor_name]`;
- `driver_race_metrics[status]`.

## 14. Страница 3: `Driver and Race Drilldown`

Цель страницы: проверить общий вывод на конкретной гонке и пилоте.

### 14.1. Фильтры страницы

Добавьте slicers:

- `races[year]`;
- `races[race_label]`;
- `drivers[driver_name]`;
- `constructors[constructor_name]`.

Для этой страницы удобно выбирать одну гонку и 1-3 пилотов.

### 14.2. Таблица пилотов в гонке

Добавьте `Table`:

- `drivers[driver_name]`;
- `constructors[constructor_name]`;
- `driver_race_metrics[starting_position_clean]`;
- `driver_race_metrics[finish_position]`;
- `driver_race_metrics[position_gain]`;
- `driver_race_metrics[position_change_group]`;
- `driver_race_metrics[relative_pace_initial_pct]`;
- `driver_race_metrics[relative_pace_middle_pct]`;
- `driver_race_metrics[relative_pace_late_pct]`;
- `driver_race_metrics[late_vs_middle_pace_improvement]`;
- `driver_race_metrics[late_vs_initial_pace_improvement]`;
- `driver_race_metrics[late_pace_improvement]`;
- `driver_race_metrics[status]`.

Отсортируйте таблицу по `finish_position` по возрастанию.

### 14.3. График позиции по кругам

Добавьте `Line chart`:

- `X-axis`: `lap_times[lap_num]`;
- `Y-axis`: `Average of lap_times[position]`;
- `Legend`: `drivers[driver_name]`.

В настройках оси Y включите обратный порядок, если доступно: позиция 1 должна быть наверху, а не внизу.

### 14.4. График времени круга

Используйте меры, созданные в разделе 10 в таблице `lap_times`:

- `Selected Driver Median Lap Time ms`;
- `Peloton Median Lap Time ms`.

Создайте `Line chart`:

- `X-axis`: `lap_times[lap_num]`;
- `Y-axis`:
  - `Selected Driver Median Lap Time ms`;
  - `Peloton Median Lap Time ms`.

Этот график показывает, когда выбранный пилот был быстрее или медленнее медианного темпа пелотона.

## 15. Страница 4: `Season and Constructor View`

Цель страницы: проверить, не создается ли эффект только отдельными гонками или командами.

### 15.1. Тренд корреляции по сезонам

Добавьте `Line chart`:

- `X-axis`: `races[year]`;
- `Y-axis`: `Spearman Correlation Position Gain vs Late vs Middle Pace Improvement`.

Если линия сильно меняется от сезона к сезону, связь нестабильна.

### 15.2. Bar chart по конструкторам

Добавьте `Clustered bar chart`:

- `Y-axis`: `constructors[constructor_name]`;
- `X-axis`: `Median Late vs Middle Pace Improvement`.

Отсортируйте по `Median Late vs Middle Pace Improvement`.

### 15.3. Scatter plot по сезонам

Добавьте `Scatter chart`:

- `X-axis`: `Median Position Gain`;
- `Y-axis`: `Median Late vs Middle Pace Improvement`;
- `Details`: `races[year]`.

Этот график помогает увидеть, какие сезоны выбиваются из общей картины.

### 15.4. Таблица сезонов

Добавьте `Table`:

- `races[year]`;
- `Race Count`;
- `Driver-Race Observations`;
- `Median Position Gain`;
- `Median Late vs Middle Pace Improvement`;
- `Gained Median Late vs Middle Pace Improvement`;
- `Spearman Correlation Position Gain vs Late vs Middle Pace Improvement`;
- `Relationship Direction`.

## 16. Финальная проверка дашборда

Перед сдачей проверьте 9 вещей.

1. В анализ попадают гонки с lap times, а не все гонки с 1950 года.
2. `race_ID` нигде не используется как признак хронологии. Для времени используйте `year`, `round`, `race_date`.
3. Первый круг исключен из расчета фазового темпа.
4. Исходное `starting_position = 0` не используется как реальная позиция; для расчета создано поле `starting_position_clean`.
5. `position_gain` считается как `starting_position_clean - finish_position`, где `starting_position_clean` - очищенная стартовая позиция.
6. Положительный `position_gain` означает, что пилот отыграл позиции.
7. Отрицательный `relative_pace_pct` означает, что пилот быстрее медианного темпа пелотона.
8. Положительный `late_vs_middle_pace_improvement` означает улучшение позднего относительного темпа относительно средней фазы.
9. При выборе сезона, гонки, пилота или конструктора все графики пересчитываются.

## 17. Как сформулировать итоговый вывод

Если гипотеза поддерживается, используйте такой шаблон:

```text
В выбранном периоде пилоты, отыгравшие позиции от старта к финишу, в среднем показывают положительное медианное улучшение позднего относительного темпа относительно средней фазы. Spearman-корреляция между `position_gain` и `late_vs_middle_pace_improvement` положительная, значит больший отыгрыш позиций обычно связан с лучшим поздним темпом относительно средней фазы. Это поддерживает гипотезу, но не доказывает причинность, потому что в модели не учтены пит-стопы, шины, Safety Car, штрафы и гоночные инциденты.
```

Если гипотеза не поддерживается, используйте такой шаблон:

```text
В выбранном периоде гипотеза не поддерживается: у группы Gained Positions медианный `late_vs_middle_pace_improvement` не положительный, либо Spearman-корреляция между `position_gain` и `late_vs_middle_pace_improvement` отрицательная. Значит, в этом срезе отыгрыш позиций не сопровождается устойчивым улучшением позднего относительного темпа относительно средней фазы и, вероятно, чаще объясняется другими факторами: стратегией, пит-стопами, сходами соперников, штрафами или обстоятельствами конкретной гонки.
```

Если результат неоднозначный:

```text
Результат требует уточнения: у группы Gained Positions может быть положительный медианный `late_vs_middle_pace_improvement`, но Spearman-корреляция слишком слабая, или наоборот. Нужно дополнительно проверить отдельные гонки, выбросы, статусы финиша и возможное влияние факторов, которых нет в датасете.
```

## 18. Частые ошибки новичков

| Ошибка | Почему это проблема |
|---|---|
| Использовать `race_ID` как порядок гонок | `race_ID` технический идентификатор, он не отражает календарь |
| Не исключить первый круг | первый круг искажает темп из-за старта и борьбы |
| Использовать `starting_position = 0` как реальную стартовую позицию | `0` означает отсутствие обычной стартовой позиции и искажает `position_gain` |
| Перепутать знак `relative_pace_pct` | меньше 0 означает быстрее, а не хуже |
| Перепутать формулу `position_gain` | нужно `starting_position_clean - finish_position`, а не наоборот |
| Считать средний темп по всем гонкам без фаз | гипотеза именно про изменение темпа по ходу гонки |
| Делать вывод только по scatter plot | нужно также смотреть группы, сезоны и конкретные гонки |
| Игнорировать статусы финиша | сходы, дисквалификации и технические проблемы могут искажать связь |

## 19. Рекомендуемое имя файла

Сохраните Power BI проект как:

```text
powerbi/F1_Driver_Pace_Analysis.pbix
```

Markdown-инструкцию можно держать рядом с `.pbix`, чтобы было понятно, как дашборд был собран.
