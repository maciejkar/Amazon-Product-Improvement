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
docker compose --profile dev up
```
As always, you need to run a `docker compose build` flag to build the image for the first time.


Open `localhost:80` then.

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

## Deployment
<details>
<summary>See the VPS deployment guide</summary>

### Initial setup

Log in to the VPS server via ssh, create a user and do the following steps. Note, that if the domain `marcinkostrzewa.online` changes it should be altered everywhere in the repo.

1. In `.bashrc` add lines:
    ```sh
    alias amazon_karczek_path="~/Amazon-Product-Improvement"
    alias cd_amazon_karczek="cd $amazon_karczek_path"
    alias karczrun="$cd_amazon_karczek && docker compose --profile full down && git pull && docker compose --profile full up -d --build"
    ```
    and run `. .bash_rc`.
2. Clone a reporsitory to the proper folder and checkout to `production`:
    ```sh
    cd_amazon_karczek
    cd ..
    git clone https://github.com/maciejkar/Amazon-Product-Improvement.git
    git checkout production
    ```
3. Create a `.env` file with at least this entry:
   ```env
   DEBUG=false
   ```
4. Add certificate with `certbot` along with a hook to copy files it to `./certs`:
   ```sh
   sudo certbot certonly --standalone -d marcinkostrzewa.online -d www.marcinkostrzewa.online --deploy-hook "cp -r /etc/letsencrypt/live/marcinkostrzewa.com $amazon_karczek_path/certs"
   ```
5. Make sure the secrets from `.github/workflows/deploy.yaml` are set correctly.

### Actions

- Run github workflow to automatically deploy the app.
- Logs are in `./app/app.log`.

</details>

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
