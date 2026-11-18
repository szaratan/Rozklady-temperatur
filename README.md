# Rozkład temperatury w pręcie paliwowym

Aplikacja Streamlit obliczająca promieniowy rozkład temperatury w paliwie i koszulce oraz osiowy rozkład gęstości mocy i temperatur.

## Uruchomienie w Windows przez uv

W PowerShellu, w folderze projektu (po zainstalowaniu `uv`):

```powershell
uv python install 3.15
uv venv --python 3.15
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Jeśli `uv` nie jest rozpoznawane w terminalu, zamknij i otwórz terminal ponownie albo użyj pełnej ścieżki do `uv.exe`.

Wartości początkowe w formularzu są przykładowe. Zastąp je danymi przyjętymi w projekcie.
