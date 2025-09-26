# collatex-critical

[![PyPI](https://img.shields.io/pypi/v/collatex-critical?color=blue\&label=PyPI)](https://pypi.org/project/collatex-critical/)
[![Python](https://img.shields.io/pypi/pyversions/collatex-critical)](https://www.python.org/)

**collatex-critical** helps scholars prepare critical editions from multiple textual witnesses, producing outputs suitable for publication.

Unlike `python-collatex`, which focuses on column-based difference visualization in XML, SVG, or HTML, `collatex-critical` produces **Markdown, PDF, HTML, and LaTeX** outputs where the **majority reading appears in the main text**, and variant readings are recorded in **footnotes or endnotes**.

---

## Features

* Multi-witness collation with clear footnote apparatus
* Output in **Markdown, PDF, HTML, and LaTeX**
* Supports multiple transliteration schemes: Devanagari, IAST, SLP1
* Integrates seamlessly with [CollateX](https://collatex.net/)
* Designed specifically for **critical editions and scholarly texts**

---

## Installation

### From PyPI

```bash
pip install collatex-critical
```

### From GitHub (development version)

```bash
pip install git+https://github.com/yourusername/collatex-critical.git
```

---

## Dependencies

1. **CollateX** (1.7.1 or later)
   Download [here](https://collatex.net/download/).
   Example: [collatex-tools-1.7.1.jar](https://oss.sonatype.org/service/local/repositories/releases/content/eu/interedition/collatex-tools/1.7.1/collatex-tools-1.7.1.jar)

2. **Pandoc**
   Install from [https://pandoc.org/installing.html](https://pandoc.org/installing.html)

3. **Indic Transliteration**

   ```bash
   pip install indic-transliteration
   ```

   Provides `indic_transliteration` Python library and `sanscript` CLI tool.

---

## Project Structure

```
input/projectName/devanagari
input/projectName/iast
input/projectName/slp1

output/projectName/devanagari
output/projectName/iast
output/projectName/slp1

collatex-tools/1.7.1/collatex-tools-1.7.1.jar
generate.sh
merger.py
```

---

## Setting Up a Project

1. Place witness texts in `input/projectName/devanagari`.
2. Name witness files according to precedence:

   * Less than 10 witnesses: `1.txt`, `2.txt`, `3.txt` …
   * 10 or more witnesses: `01.txt`, `02.txt`, `03.txt` …
3. **File order indicates descending precedence** (first file = highest authority).

---

## Running the Project

```bash
sh generate.sh projectName
```

* Creates missing directories under `input/` and `output/`.
* Generates outputs in all available transliteration schemes.
* Input witness files must exist prior to running.

---

## Output

For each project:

* `projectName.md`, `projectName.pdf`, `projectName.tex`, `projectName.html`
  → `output/projectName/devanagari/`

* Corresponding outputs in other transliterations:
  → `output/projectName/iast/` and `output/projectName/slp1/`

---

## Collation Logic

1. **Majority Rule:** Reading preferred by the majority appears in the main text; others appear in footnotes.
2. **Tie-Breaker:** If no clear majority, the order of precedence determines the main reading (`01.txt` > `02.txt` > …).

> The choice of the most faithful witness is left to the editor’s discretion (e.g., oldest, most accurate, or scholarly judgment).

---

## Contributing

Contributions are welcome:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add feature"`
4. Push your branch: `git push origin feature/my-feature`
5. Open a pull request

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---


