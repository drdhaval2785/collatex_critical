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
pip install git+https://github.com/drdhaval2785/collatex-critical.git
```

---

## Dependencies

1. **Java** - Java Runtime Environment (JRE) version 8 or higher is needed to run Collatex jar file.

2. **CollateX** (1.7.1 or later)
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
4. Make sure that collatex-tools/1.7.1/collatex-tools-1.7.1.jar is in the same folder as generate.sh file.

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

## Checking your installation

The github repository has a test data in input/test/devanagari/ directory.

It carries three witnesses of a manuscript.

Run the following from your commandline `sh generate.sh test`.

If everything goes as expected, you should see the output in output/test directory.

If there is any error logged, make sure you have installed the necessary dependencies and have the collatex-tools/1.7.1/collatex-tools-1.7.1.jar file at the correct location.

## Example output

### PDF

<img width="456" height="661" alt="image" src="https://github.com/user-attachments/assets/c2b846ea-3f3e-4e4f-a2f6-564d4da3994b" />

### HTML

<img width="663" height="214" alt="Screenshot_2025-09-27_12-12-57" src="https://github.com/user-attachments/assets/dd51656c-c5a9-4ea7-bc5a-a5a7d5752629" />


## Contributing

Contributions are welcome:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add feature"`
4. Push your branch: `git push origin feature/my-feature`
5. Open a pull request

---

## License

GNU GPL v3.0. See [LICENSE](LICENSE) for details.

---


