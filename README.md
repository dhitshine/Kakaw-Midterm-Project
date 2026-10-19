# Kakaw-Midterm-Project
> Penjadwalan Kelas Mata Kuliah Menggunakan Pendekatan Local Search Optimization.

<p align="center">
<a href="/doc">Project Report</a>
</p>

---

## Team
Kelompok 5: Kakaw

<div align="center" id="contributor">

### Contributors

<table align="center">
  <tr align="left">
    <td><b>NRP</b></td>
    <td><b>Name</b></td>
    <td align="center"><b>GitHub</b></td>
  </tr>
  <tr align="left">
    <td>5025251204</td>
    <td>Althof Rahmatullah</td>
    <td align="center">
      <a href="https://github.com/Linney1">
        <img src="https://github.com/Linney1.png" width="48" alt="Linney1"/><br/>
        <sub><b> @Linney1 </b></sub>
      </a>
    </td>
  </tr>
  <tr align="left">
    <td>5025251183</td>
    <td>Aditya Hariyadi Tjujitno</td>
    <td align="center">
      <a href="https://github.com/adityahariyadit-hash">
        <img src="https://github.com/adityahariyadit-hash.png" width="48" alt="adityahariyadit-hash"/><br/>
        <sub><b> @adityahariyadit-hash </b></sub>
      </a>
    </td>
  </tr>
  <tr align="left">
    <td>5025251084</td>
    <td>Radhit Akriandra</td>
    <td align="center">
      <a href="https://github.com/dhitshine">
        <img src="https://github.com/dhitshine.png" width="48" alt="dhitshine"/><br/>
        <sub><b> @dhitshine </b></sub>
      </a>
    </td>
  </tr>
  <tr align="left">
    <td>5025251206</td>
    <td>Rexa Matutu Harsaputra</td>
    <td align="center">
      <a href="https://github.com/rexaeca">
        <img src="https://github.com/rexaeca.png" width="48" alt="rexaeca"/><br/>
        <sub><b> @rexaeca </b></sub>
      </a>
    </td>
  </tr>
  <tr align="left">
    <td>5025251211</td>
    <td>Rizqi Ardiansyah Putra P.</td>
    <td align="center">
      <a href="https://github.com/Ciko1140">
        <img src="https://github.com/Ciko1140.png" width="48" alt="Ciko1140"/><br/>
        <sub><b> @Ciko1140 </b></sub>
      </a>
    </td>
  </tr>
</table>

</div>

## Description
Kakaw adalah sistem penjadwalan kelas mata kuliah paralel dengan menggunakan pendekatan local search yang diimplementasikan sebagai *Midterm Project* mata kuliah Konsep Kecerdasan Artifisial (EK234201).

Tiga algoritma local search yang diimplementasikan, yaitu:
1. Steepest-Ascent Hill Climbing
2. Simulated Annealing
3. Genetic Algorithm

## Project Structure
```
.
├── doc
│   ├── Laporan.pdf                       # Laporan
│   └── Slide.pdf                         # Slide
├── src
│   └── kakaw
│       ├── __init__.py                   # CLI & main
│       ├── algorithms
│       │   ├── __init__.py
│       │   ├── base.py                   # Abstract class LocalSearch
│       │   ├── genetic_algorithm.py      # Genetic Algorithm
│       │   ├── simulated_annealing.py    # Simulated Annealing
│       │   └── steepest_hill_climbing.py # Steepest-Ascent Hill Climbing
│       ├── models
│       │   ├── __init__.py
│       │   ├── allocation.py             # Allocation (hari, mulai, ruangan)
│       │   ├── constants.py              # Konstanta waktu & bobot prioritas
│       │   ├── course_class.py           # CourseClass
│       │   ├── instance.py               # Instance data tetap
│       │   ├── room.py                   # Room
│       │   └── student.py                # Student & Enrollment
│       ├── problems
│       │   ├── __init__.py
│       │   ├── objective.py              # ObjectiveFunction
│       │   ├── problem.py                # Problem & successor functions
│       │   └── state.py                  # State
│       └── utils
│           ├── __init__.py
│           ├── formatter.py              # PrettyTable schedule formatter
│           └── parser.py                 # JSON Parser
├── tests                                 $ Tests Case
├── pyproject.toml                        # Metadata project
├── .python-version                      
├── .gitignore                          
├── uv.lock
└── README.md
```

## Requirements
- Python Versions 3.14 or newer
- uv Versions 0.12 or newer (recommended package manager)

## Installation
- Clone repositorinya
  ```sh
  git clone https://github.com/dhitshine/Kakaw-Midterm-Project.git && cd Kakaw-Midterm-Project
  ```
- Buat virtual environtment dengan `uv`
  ```sh
  uv venv
  ```
- Install dependencies
  ```sh
  uv sync
  ```
## Usage
### Steepest Ascent Hill-Climbing
```sh
uv run kakaw --test tests/sample.json --algorithm steepest-hc --plot output.png
```
### Simulated Annealing
```sh
uv run kakaw --test tests/sample.json --algorithm simulated --plot output.png
```
### Genetic Algorithm
```sh
uv run kakaw --test tests/sample.json --algorithm genetic --plot output.png
```
### Help
```sh
uv run kakaw --help
```
