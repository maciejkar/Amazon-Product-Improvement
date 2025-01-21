![GitHub last commit](https://img.shields.io/github/last-commit/maciejkar/Amazon-Product-Improvement)

# Amazon Product Improvement Analyzer

A tool that analyzes scrapes Amazon product reviews and suggests product improvements using LangChain and LLMs.

## Features

- Product comments and details scraping from url
- Product analysis using LangChain
- Web interface built with Streamlit

## License

[![Licence](https://img.shields.io/github/license/Ileriayo/markdown-badges?style=for-the-badge)](./LICENSE)


## Development Setup

Set up the env variables by copying `./sample.dev.env` to `./.env`. You can alter the variables here, eg. debug mode or the selenium browser mode (headful/headless).

### A. In container (recommended)

In the main directory run
```sh
docker compose up
```
As always, you might need to add a `--build` flag to build the image for the first time.

#### Issues

❗ Sometimes logging to Amazon does not work, but after container restart everything is fine.

### B. Locally

1. Install requirements for Python 3.10:
```bash
pip install -r requirements.txt
```
2. Install Chrome for Selenium drivers.
3. Run the app
```bash
cd app
streamlit run runapp.py
```

## Technologies

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Selenium](https://img.shields.io/badge/-selenium-%43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![Google Gemini](https://img.shields.io/badge/google%20gemini-8E75B2?style=for-the-badge&logo=google%20gemini&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)


## Authors
- [Maciej Karczewski](https://github.com/maciejkar)
- [Mateusz Machaj](https://github.com/o-mateo-o)
- [Hela Ghorbel](https://github.com/hela2509)