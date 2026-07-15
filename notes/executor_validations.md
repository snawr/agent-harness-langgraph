Uważam, że warto zaprojektować executora jako **uniwersalny silnik walidacji**, a nie jako "node uruchamiający pytest". Wtedy będzie działał zarówno dla prostego kalkulatora, jak i dla dużego projektu Python.

Podzieliłbym walidację na kilka poziomów.

# Poziom 1 — Patch

To już robisz.

Sprawdzenie:

* czy diff został zastosowany,
* czy nie było konfliktów,
* które pliki zostały zmienione.

Jeżeli to się nie udało, kończysz pracę executora.

---

# Poziom 2 — Integralność projektu

To są bardzo szybkie testy.

Przykładowo:

Python

```
python -m compileall .
```

lub

```
python -m py_compile file.py
```

To wykrywa błędy typu

```
SyntaxError
IndentationError
```

bez uruchamiania programu.

---

# Poziom 3 — Import

Często kod jest poprawny składniowo, ale nie daje się zaimportować.

Np.

```
ModuleNotFoundError
ImportError
AttributeError
```

Można próbować zaimportować główny moduł.

---

# Poziom 4 — Testy

Jeżeli repo zawiera testy:

```
pytest
```

Jeżeli nie zawiera — pomijasz.

To powinno być automatyczne.

---

# Poziom 5 — Lint

Opcjonalnie.

```
ruff check .
```

albo

```
flake8
```

Nie traktowałbym błędów linta jako porażki zadania.

Raczej warning.

---

# Poziom 6 — Type checking

Jeżeli projekt używa mypy.

```
mypy .
```

Znowu — raczej warning.

---

# Poziom 7 — Build

Jeżeli projekt posiada etap build.

Np.

```
npm run build
cargo build
cmake
```

Executor nie powinien wiedzieć jaki to język.

Powinien dostać komendy do wykonania.

---

# Poziom 8 — Smoke test

To moim zdaniem najważniejsza część.

Dla kalkulatora:

```
echo "2\n3\n+" | python calculator.py
```

i sprawdzenie

```
5
```

Dla API:

```
curl localhost:8000/health
```

Dla biblioteki:

```
python examples/basic.py
```

Dla CLI:

```
python main.py --help
```

To daje dużo większą pewność niż sam pytest.

---

# Poziom 9 — Własne komendy

To powinien być docelowy mechanizm.

Planner może zwracać np.

```
Validation:

- pytest -q
- python examples/example.py
- python benchmark.py
```

Executor tylko wykonuje.

---

# Jak przebudowałbym state

Obecnie masz tylko

```
last_command
```

To będzie za mało.

Za chwilę executor będzie wykonywał kilka komend.

Dałbym raczej

```
execution_results: List[CommandResult]
```

i

```
validation_summary
```

gdzie np.

```
syntax_ok = True
tests_ok = False
lint_ok = True
build_ok = True
```

---

# Dodałbym jeszcze jedną strukturę

Coś w rodzaju

```
ValidationStep
```

np.

```
name
command
required
timeout
```

Przykład:

```
[
    {
        "name": "syntax",
        "command": "python -m compileall .",
        "required": True
    },
    {
        "name": "tests",
        "command": "pytest -q",
        "required": True
    },
    {
        "name": "ruff",
        "command": "ruff check .",
        "required": False
    }
]
```

Executor robi wtedy po prostu:

```
for validation in validations:
    run_command(...)
```

Nie ma żadnych `if repo_has_pytest`.

---

# Co robić przy bardziej złożonych zadaniach?

Największym ograniczeniem obecnego projektu nie jest executor, ale to, że **agent nie wie, jak zweryfikować wykonanie zadania**.

Przykład:

> Dodaj endpoint `/users`.

Samo:

```
pytest
```

może nic nie sprawdzić.

Potrzebujesz testu funkcjonalnego:

```
uvicorn app:app &
curl /users
```

lub

```
python integration_test.py
```

Dlatego większość nowoczesnych agentów (Codex, Claude Code, Aider) nie próbuje odgadywać walidacji. Planner lub użytkownik definiuje plan wykonania oraz plan weryfikacji, a executor jedynie realizuje ten plan.

## Co zmieniłbym już teraz

Na etapie MVP wprowadziłbym trzy zmiany:

1. Zastąpił `last_command` listą `execution_results`, aby przechowywać wyniki wszystkich wykonanych kroków walidacji.
2. Dodał do stanu `validation_plan`, zawierający listę komend do uruchomienia wraz z informacją, czy ich niepowodzenie jest krytyczne (`required`).
3. Nie kodowałbym logiki typu „uruchom pytest” bezpośrednio w executorze. Executor powinien być prostym wykonawcą planu walidacji. Dzięki temu ten sam node będzie działał zarówno dla prostego kalkulatora, jak i dla złożonych projektów wielomodułowych.
