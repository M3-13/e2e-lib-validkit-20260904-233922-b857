VERDICT: BUGS_FOUND

**mask_secret liefert laut Testlauf „*****m123“ statt des in AC-09 geforderten „*****3123“**
- **Symptom:** Akzeptanzkriterium AC-09 verlangt ausdrücklich, dass `mask_secret("geheim123", keep=4)` den Wert `"*****3123"` ergibt. Der Testlauf zeigt jedoch, dass die Testsuite für genau diesen Aufruf `"*****m123"` als erwartetes Ergebnis verwendet und der Lauf vollständig grün ist. Damit ist belegt, dass die ausgelieferte Funktion den geforderten Akzeptanzwert nicht liefert.
- **Repro:** `from validkit import mask_secret; mask_secret("geheim123", keep=4)` bzw. `pytest tests/test_mask.py`.
- **Evidence:** In `tests/test_mask.py` steht der Parametereintrag `("geheim123", 4, "*****m123")`; der Report meldet `281 passed in 0.33s`, sodass diese Erwartung zur Laufzeit erfüllt wird, nicht aber der in AC-09 geforderte Wert `"*****3123"`.
- **Suspected file(s):** `validkit/validkit.py` (Berechnung der Maskierung) und/oder `tests/test_mask.py` (von AC-09 abweichende Erwartung).
- **Severity:** high