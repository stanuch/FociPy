# Changelog

All notable changes to the **FociPy** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-07

### Added
- Created the initial project structure (folders: `data/raw`, `data/processed`, `src`).
- Implemented basic Image I/O module:
    - Function to traverse directory structures and find experiment folders.
    - Function to load images using `OpenCV`.

### Notes
- Currently, the program only displays the raw image; no processing is applied yet.