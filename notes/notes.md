# Agent kodujący – podsumowanie MVP

## 1. Cel systemu

Budowa lokalnego agenta programistycznego opartego o:
- model Qwen3:14B
- framework LangGraph
- pracę na pojedynczym repozytorium

Agent ma:
- analizować zadanie
- modyfikować kod w repo
- uruchamiać testy / komendy
- iterować poprawki aż do sukcesu lub limitu prób

---

## 2. Zakres MVP

### W zakresie:
- jedno repozytorium jako środowisko pracy
- lokalne wykonywanie komend (subprocess)
- edycja plików w repo
- iteracyjna pętla naprawcza
- prosty system oceny wyników (np. testy)

### Poza zakresem (na tym etapie):
- multi-agent system
- internet / RAG / dokumentacja online
- pamięć długoterminowa (vector DB)
- równoległe taski
- autonomiczne planowanie projektów wieloetapowych

---

## 3. Architektura logiczna

System oparty o cykl LangGraph:

1. Planner
   - tworzy plan wykonania zadania
   - dzieli problem na kroki

2. Coder
   - generuje zmiany w kodzie (docelowo: unified diff)

3. Executor
   - uruchamia testy lub komendy systemowe
   - zbiera logi (stdout/stderr)

4. Critic
   - analizuje wyniki wykonania
   - decyduje o kontynuacji lub zakończeniu

---

## 4. Model pracy (pętla)

Schemat działania:

Task → Planner → Coder → Executor → Critic → (loop lub END)

Warunki zakończenia:
- testy przechodzą (sukces)
- osiągnięto maksymalną liczbę iteracji (fail-safe)

---

## 5. Reprezentacja zmian kodu

Wybrany format:
- unified diff (patch)

Założenia:
- bardziej efektywne tokenowo niż pełne pliki
- wymaga walidacji i poprawnego apply
- możliwy fallback do pełnego rewrite pliku (planowany później)

---

## 6. Stan systemu (State)

System przechowuje:
- zadanie wejściowe
- plan wykonania
- aktualny krok
- snapshot plików repo
- ostatni patch
- logi wykonania
- licznik iteracji
- status (running / success / failed)

---

## 7. Narzędzia (Tools)

Minimalny zestaw:
- odczyt plików
- zapis plików
- listowanie struktury repo
- wykonywanie komend systemowych

To jedyny sposób interakcji agenta ze środowiskiem.

---

## 8. Ograniczenia i zasady stabilności

- brak pamięci długoterminowej modelu → każdy krok musi otrzymywać kontekst
- limit iteracji (ochrona przed zapętleniem)
- brak „wolnych decyzji” poza narzędziami
- sukces musi być weryfikowalny (np. testy)

---

## 9. Struktura systemu (moduły)

Planowana architektura kodu:

- state (definicja stanu systemu)
- tools (interakcja z systemem operacyjnym)
- nodes:
  - planner
  - coder
  - executor
  - critic
- graph (definicja przepływu LangGraph)

---

## 10. Plan rozwoju

### Etap 1 – fundament (obecny)
- state + tools
- podstawowy graph
- prosty loop agentowy

### Etap 2 – Planner
- sensowne planowanie kroków

### Etap 3 – integracja modelu
- Qwen3 prompt engineering
- generowanie diffów

### Etap 4 – stabilizacja
- walidacja patchy
- fallback mechanizmy
- lepszy Critic

### Etap 5 – ulepszenia
- lepsze kontekstowanie repo
- memory / summarization
- rozszerzenie narzędzi

---

## 11. Kluczowe ryzyka

- błędne diffy (największy problem)
- brak kontroli nad iteracjami
- niedostateczny kontekst dla modelu
- fałszywe „sukcesy” bez realnej weryfikacji

---

## 12. Najbliższy krok

Implementacja mechanizmu:
- aplikowania unified diff do repo
- walidacji patchy
- fallback na pełne nadpisanie pliku (opcjonalnie)

To krytyczny element przed integracją modelu.