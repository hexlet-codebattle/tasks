# Grand Slam S3 2026: Осень в живой природе

## Общая тема

Задачи посвящены естественным процессам сентября и октября. Каждый сюжет знакомит участника с биологическим понятием, а математическая модель этого понятия превращается в алгоритмическую задачу.

Специальные знания для решения не нужны: научный контекст даёт новый факт, а короткое условие точно задаёт используемую модель. Набор охватывает числа, время, строки, массивы, частотные таблицы, интервалы, сетки, графы, динамическое программирование и поиск кратчайшего пути.

## Задачи

### 1. `daylight_loss`

**Уровень:** `elementary`

**Описание:** Фотопериод — продолжительность светлой части суток; его осеннее сокращение служит для многих организмов сигналом к миграции, линьке или переходу в состояние покоя. Наблюдения за сентябрь и октябрь заданы как `[sunrise, sunset]` в минутах от полуночи. Найдите, на сколько минут световой день стал короче.

**Алгоритм:** Вычислить продолжительность каждого дня как разность заката и восхода, затем вычесть октябрьское значение из сентябрьского.

**Решение:**

```python
def solution(september: list[int], october: list[int]) -> int:
    return september[1] - september[0] - october[1] + october[0]
```

```python
solution([360, 1110], [420, 1020]) == 150
solution([390, 1080], [400, 1070]) == 20
```

### 2. `growing_degree_target`

**Уровень:** `easy`

**Описание:** Фенологи оценивают развитие растений по сумме активных температур: день с температурой `t` добавляет `max(0, t - base)` единиц тепла выше базового порога. Верните первый индекс, на котором накоплено не меньше `target`, или $-1$.

**Алгоритм:** Последовательно накапливать вклад каждого дня. Сразу вернуть индекс, когда сумма впервые достигнет `target`.

**Решение:**

```python
def solution(temperatures: list[int], base: int, target: int) -> int:
    total = 0
    for i, temperature in enumerate(temperatures):
        total += max(0, temperature - base)
        if total >= target:
            return i
    return -1
```

```python
solution([5, 6, 7], 10, 1) == -1
solution([8, 12, 15, 9], 10, 7) == 2
```

### 3. `ripe_berry_streak`

**Уровень:** `easy`

**Описание:** При созревании многих плодов растёт содержание растворимых сахаров, поэтому его используют как один из показателей зрелости. Ягода считается зрелой при значении не меньше `min_sugar`. Найдите самый длинный непрерывный участок зрелых ягод на ветке.

**Алгоритм:** Пройти по массиву, увеличивая длину текущей серии зрелых ягод и обнуляя её на незрелой. Одновременно хранить максимальную длину.

**Решение:**

```python
def solution(sugar: list[int], min_sugar: int) -> int:
    best = run = 0
    for value in sugar:
        run = run + 1 if value >= min_sugar else 0
        best = max(best, run)
    return best
```

```python
solution([4, 5, 6], 7) == 0
solution([8, 12, 11, 5, 10], 10) == 2
```

### 4. `bird_call_encoding`

**Уровень:** `easy`

**Описание:** Контактные позывы помогают птицам в стае не терять друг друга, а тревожные предупреждают об опасности. В записи биоакустика `C` означает контактный позыв, `A` — тревожный, `S` — тишину. Сожмите каждую группу одинаковых событий в символ и длину группы.

**Алгоритм:** Читать строку слева направо и собирать соседние одинаковые символы в группы. Для каждой группы записать символ и количество повторений.

**Решение:**

```python
def solution(recording: str) -> str:
    groups = []
    for event in recording:
        if groups and groups[-1][0] == event:
            groups[-1][1] += 1
        else:
            groups.append([event, 1])
    return "".join(f"{event}{count}" for event, count in groups)
```

```python
solution("") == ""
solution("CCAAS") == "C2A2S1"
```

### 5. `first_frost_period`

**Уровень:** `easy`

**Описание:** Одно холодное утро и устойчивое похолодание действуют на организмы по-разному, поэтому фенологическая модель учитывает серию холодных дней. Найдите первый день, с которого температура не превышает `threshold` в течение `days` дней подряд. Если такого периода нет, верните $-1$.

**Алгоритм:** Поддерживать длину текущей серии холодных дней, сбрасывая её при превышении порога. При достижении длины `days` восстановить индекс начала серии.

**Решение:**

```python
def solution(temperatures: list[int], threshold: int, days: int) -> int:
    run = 0
    for i, temperature in enumerate(temperatures):
        run = run + 1 if temperature <= threshold else 0
        if run == days:
            return i - days + 1
    return -1
```

```python
solution([5, 8, 5], 6, 2) == -1
solution([9, 3, 2, 4], 4, 3) == 1
```

### 6. `unrecovered_seed_caches`

**Уровень:** `easy`

**Описание:** Белки распределяют запасы по множеству тайников, а забытые семена иногда прорастают и помогают расселению деревьев. Метка тайника записывается при захоронении и повторно при извлечении семени. Верните в алфавитном порядке метки с нечётным количеством записей.

**Алгоритм:** Подсчитать частоту каждой метки, оставить метки с нечётной частотой и отсортировать их.

**Решение:**

```python
def solution(tags: list[str]) -> list[str]:
    from collections import Counter
    return sorted(tag for tag, count in Counter(tags).items() if count % 2)
```

```python
solution(["oak", "oak"]) == []
solution(["pine", "oak", "pine", "birch"]) == ["birch", "oak"]
```

### 7. `leaf_pigment_transitions`

**Уровень:** `medium`

**Описание:** Осенью хлорофилл разрушается, становятся заметны каротиноиды, а у многих видов образуются красные антоцианы. Каждое наблюдение содержит количества этих трёх пигментов с единственным максимумом. Удалите минимум наблюдений, чтобы преобладающий пигмент шёл без возврата в порядке `green → yellow → red`.

**Алгоритм:** Заменить каждое наблюдение номером преобладающего пигмента: $0$, $1$ или $2$. Динамикой найти самую длинную неубывающую подпоследовательность из этих трёх состояний; остальные наблюдения удалить.

**Решение:**

```python
def solution(pigments: list[list[int]]) -> int:
    states = [max(range(3), key=amounts.__getitem__) for amounts in pigments]
    best = [0, 0, 0]
    for state in states:
        best[state] = 1 + max(best[:state + 1])
    return len(states) - max(best, default=0)
```

```python
solution([[5, 2, 1], [2, 5, 1], [1, 2, 5]]) == 0
solution([[1, 2, 5], [5, 2, 1], [1, 5, 2]]) == 1
```

### 8. `mushroom_growth_days`

**Уровень:** `medium`

**Описание:** Видимый гриб — спороносное плодовое тело, а основная часть организма существует как мицелий; для плодоношения многим видам нужна достаточная влажность. В модели плодовые тела появляются, когда сумма осадков за последние `window` дней не меньше `min_rain`. Верните индексы всех таких дней.

**Алгоритм:** Построить префиксные суммы осадков. Для каждого полного окна получать его сумму вычитанием двух префиксов за $O(1)$.

**Решение:**

```python
def solution(rain: list[int], window: int, min_rain: int) -> list[int]:
    prefix = [0]
    for amount in rain:
        prefix.append(prefix[-1] + amount)
    return [i for i in range(window - 1, len(rain))
            if prefix[i + 1] - prefix[i + 1 - window] >= min_rain]
```

```python
solution([1, 1, 1], 2, 5) == []
solution([2, 3, 1, 4], 2, 5) == [1, 3]
```

### 9. `windborne_seed_landings`

**Уровень:** `medium`

**Описание:** Распространение семян ветром называется анемохорией: крылатки и семена с «парашютиками» удаляются от родительского растения, но прорастают только в подходящих местах. После сдвига всех семян на `wind` посчитайте попавшие хотя бы в один замкнутый плодородный интервал. Интервалы могут пересекаться.

**Алгоритм:** Отсортировать и объединить пересекающиеся плодородные интервалы. Для позиции каждого семени бинарным поиском найти последний интервал, начинающийся не правее неё, и проверить его правую границу.

**Решение:**

```python
def solution(seeds: list[int], wind: int, fertile: list[list[int]]) -> int:
    from bisect import bisect_right
    intervals = []
    for left, right in sorted(fertile):
        if intervals and left <= intervals[-1][1]:
            intervals[-1][1] = max(intervals[-1][1], right)
        else:
            intervals.append([left, right])
    starts = [left for left, _ in intervals]
    count = 0
    for seed in seeds:
        i = bisect_right(starts, seed + wind) - 1
        count += i >= 0 and seed + wind <= intervals[i][1]
    return count
```

```python
solution([1, 2], 10, [[0, 5]]) == 0
solution([0, 5, 10], 2, [[1, 3], [7, 9]]) == 2
```

### 10. `mycelium_colonies`

**Уровень:** `medium`

**Описание:** Мицелий состоит из разветвлённых нитей — гиф — и может годами жить в почве без видимых плодовых тел. На карте `M` обозначает участок мицелия, а `.` — пустое место. Соприкасающиеся стороной или углом участки образуют одну колонию. Найдите количество колоний.

**Алгоритм:** Хранить все клетки `M` в множестве. Пока оно не пусто, начинать обход в глубину из любой клетки, удалять всю связанную компоненту и увеличивать число колоний.

**Решение:**

```python
def solution(forest: list[str]) -> int:
    cells = {(r, c) for r, row in enumerate(forest) for c, x in enumerate(row) if x == "M"}
    colonies = 0
    while cells:
        colonies += 1
        stack = [cells.pop()]
        while stack:
            r, c = stack.pop()
            near = {(r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                    if (dr or dc) and (r + dr, c + dc) in cells}
            cells -= near
            stack += near
    return colonies
```

```python
solution(["M.M"]) == 2
solution(["MM.", "..M"]) == 1
```

### 11. `bird_migration_stops`

**Уровень:** `medium`

**Описание:** Во время миграционных остановок птицы отдыхают и пополняют энергетические запасы, поэтому потеря ключевых мест может разорвать длинный маршрут. Первая и последняя точки — начало и конец перелёта, остальные — места отдыха. Птица пролетает не больше `max_distance` за раз. Найдите минимум остановок или верните $-1$.

**Алгоритм:** Считать точки вершинами графа, соединяя пары на допустимом расстоянии. Поиск в ширину даст минимальное количество перелётов; число промежуточных остановок на один меньше.

**Решение:**

```python
def solution(points: list[list[int]], max_distance: int) -> int:
    queue = [(0, 0)]
    seen = {0}
    for point, flights in queue:
        if point == len(points) - 1:
            return flights - 1
        for other in range(len(points)):
            distance = ((points[point][0] - points[other][0]) ** 2 +
                        (points[point][1] - points[other][1]) ** 2)
            if other not in seen and distance <= max_distance ** 2:
                seen.add(other)
                queue.append((other, flights + 1))
    return -1
```

```python
solution([[0, 0], [5, 0]], 3) == -1
solution([[0, 0], [3, 0], [6, 0]], 3) == 1
```

### 12. `peak_leaf_abscission`

**Уровень:** `medium`

**Описание:** Перед листопадом у основания черешка формируется зона абсциссии; когда связь ослабевает, ветер и дождь помогают листу отделиться. Для каждого дерева дан включительный интервал дней листопада. Верните `[day, count]` для самого раннего дня с максимальным количеством одновременно сбрасывающих листья деревьев.

**Алгоритм:** Создать события `+1` в начале каждого интервала и `-1` на следующий день после его конца. Просуммировать события по дням и запомнить первое достижение максимума.

**Решение:**

```python
def solution(intervals: list[list[int]]) -> list[int]:
    if not intervals:
        return [-1, 0]
    events = {}
    for start, end in intervals:
        events[start] = events.get(start, 0) + 1
        events[end + 1] = events.get(end + 1, 0) - 1
    active = best = 0
    best_day = -1
    for day in sorted(events):
        active += events[day]
        if active > best:
            best_day, best = day, active
    return [best_day, best]
```

```python
solution([]) == [-1, 0]
solution([[1, 3], [2, 4], [4, 5]]) == [2, 2]
```

### 13. `migration_weather_plan`

**Уровень:** `hard`

**Описание:** Многие птицы откладывают вылет при плохой погоде и используют попутный ветер для экономии энергии. `costs[day][segment]` задаёт расход на следующий участок, а $-1$ запрещает полёт. За день птица отдыхает или проходит один участок. Найдите минимальный расход или верните $-1$.

**Алгоритм:** Динамика хранит минимальную энергию для прохождения каждого количества участков к началу дня. Для нового дня рассмотреть отдых и переход через следующий доступный участок.

**Решение:**

```python
def solution(costs: list[list[int]]) -> int:
    segments = len(costs[0])
    infinity = float("inf")
    dp = [0] + [infinity] * segments
    for day in costs:
        next_dp = dp[:]
        for segment, energy in enumerate(day):
            if energy >= 0:
                next_dp[segment + 1] = min(next_dp[segment + 1],
                                           dp[segment] + energy)
        dp = next_dp
    return -1 if dp[-1] == infinity else dp[-1]
```

```python
solution([[1, 5], [2, 1]]) == 2
solution([[-1], [3]]) == 3
```

### 14. `windborne_seed_path`

**Уровень:** `hard`

**Описание:** Направление воздушных потоков определяет траекторию ветрораспространяемых семян. Каждая клетка содержит направление ветра `U`, `D`, `L` или `R`: перелёт по ветру стоит $0$ энергии, а в другом направлении — $1$. Найдите минимальную стоимость пути к правому нижнему углу.

**Алгоритм:** Представить клетки вершинами графа с рёбрами веса $0$ или $1$. Использовать поиск в ширину 0–1: бесплатные переходы добавлять в начало очереди, остальные — в конец.

**Решение:**

```python
def solution(wind: list[str]) -> int:
    from collections import deque
    height, width = len(wind), len(wind[0])
    distance = [[float("inf")] * width for _ in range(height)]
    distance[0][0] = 0
    queue = deque([(0, 0)])
    directions = [(0, 1, "R"), (1, 0, "D"), (0, -1, "L"), (-1, 0, "U")]
    while queue:
        row, column = queue.popleft()
        for dr, dc, direction in directions:
            nr, nc = row + dr, column + dc
            if 0 <= nr < height and 0 <= nc < width:
                cost = wind[row][column] != direction
                new_distance = distance[row][column] + cost
                if new_distance < distance[nr][nc]:
                    distance[nr][nc] = new_distance
                    if cost:
                        queue.append((nr, nc))
                    else:
                        queue.appendleft((nr, nc))
    return distance[-1][-1]
```

```python
solution(["RD", "LL"]) == 0
solution(["LL", "UU"]) == 2
```

## Научные материалы

- [USDA: модель сумм активных температур](https://www.ars.usda.gov/plains-area/temple-tx/grassland-soil-and-water-research-laboratory/docs/193226)
- [US Forest Service: почему листья меняют цвет](https://www.fs.usda.gov/Internet/FSE_DOCUMENTS/stelprd3817419.pdf)
- [US Forest Service: грибы, плодовые тела и мицелий](https://research.fs.usda.gov/treesearch/38089)
- [Cornell Lab of Ornithology: основы миграции птиц](https://www.allaboutbirds.org/news/the-basics-how-why-and-where-of-bird-migration/)
- [Cornell Lab of Ornithology: роль миграционных остановок](https://www.allaboutbirds.org/news/bottlenecks-refueling-stations-and-fire-escapes-3-types-of-stopover-sites-migrants-really-need/)
- [Smithsonian Science Education Center: тайники белок и распространение семян](https://ssec.si.edu/node/769)
- [University of Georgia Extension: зона абсциссии и листопад](https://site.extension.uga.edu/forsyth/trees-that-hold-their-leaves/)
