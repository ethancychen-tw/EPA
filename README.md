# EPA project

## Resources
[Video DEMO](https://www.youtube.com/watch?v=nB1bcGiC-Fg)
[What's EPA](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3613304/)

## Requirements
Python >= 3.8
## Setup guide
1. Get a config.env file
2. Create an virtual environment
> python -m venv venv
3. Enter virtual env
> source venv/bin/activate
4. Install poetry
> pip install poetry
5. Poetry install (If you don't want linter and other dev tools, specify --no-dev in the option)
> poetry install
6. Run locally
> python run.py

## Deploy
> zappa deploy
