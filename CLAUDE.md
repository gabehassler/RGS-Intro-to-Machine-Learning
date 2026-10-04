# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

This is a **public GitHub repository** for *Machine Learning and Data Science for Policy Analysis*, taught by Carter Price and Gabe Hassler at the [RAND School of Public Policy](https://www.rand.edu). It holds course materials (e.g., slides, notebooks, assignments, datasets, the syllabus) for use by instructors and students. Claude Code is used here to help manage and develop these course materials. See `README.md` for student-facing setup instructions and `RGS-intro-to-ml-syllabus_final.pdf` for the full syllabus (schedule, readings, grading, policies).

Because the repo is public, do not commit sensitive information (e.g., student grades/PII, unpublished exam solutions meant to stay private, credentials).

## Git workflow

Do work on the `working` branch, not `main`. The user merges `working` into `main` manually — do not merge or push to `main` yourself.

## Repository structure

- `code/` — standalone, numbered Python scripts shared across the course (e.g., data download/build scripts). **Run all scripts from the repository root**, not from inside `code/` (e.g., `python code/02_download_data.py`).
- `assignments/` — one directory per assignment (e.g., `HW_01/`), containing the Quarto `.qmd` source and rendered output.
- `documentation/` — supporting reference docs, including `data_dictionaries/` (generated variable metadata).
- Python dependencies are tracked in `requirements.txt` (hand-edited, top-level packages only) and `requirements-lock.txt` (full pinned environment via `pip freeze`); the virtual environment lives in `.venv`.
- `_quarto.yml` / `_environment` configure the Quarto project build.

## Status

Course content (code, assignments, documentation) is actively being added. Keep this section in sync as structure, tooling, and conventions evolve.
