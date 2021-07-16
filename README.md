# alpha-rhythm
Gambler Engagement Extraction (based on alpha rhythm)
- environment.ipynb - extraction of engagement increase/decrease based on extracted alpha and user actions. This file contains the base result currently
- eeg-converter.ipynb - conversion of raw EEG files given events file and OpenBCI data. Contains denoising procedures as well.
- band-power-jolu.ipynb - scratch file, contains some work related to player states extraction using Hidden Markov Model
- band-power-baseline-sasha.ipynb - an example of baseline task - with eyes closed and opened

## Instruction
- Download subject-* directories to ./valid-data dir
- Run all cells in eeg-converter.ipynb to get files with events and related alpha rhythm
- Run all cells in environment.ipynb to get user engagement change for action-state space

## References
[1] [Neural correlates of flow, boredom, and anxiety in gaming](https://scholarsmine.mst.edu/cgi/viewcontent.cgi?article=8812&context=masters_theses)
