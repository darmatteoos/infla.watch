# infla.watch
Small web app for checking Italian supermarket prices inflation and shrinkflation

steps to run the app:

create a venv virtual environment for python in the root directory of the project 
and install all the necessary dependencies with the command:
`pip install -r requirements.txt`

create a renv virtual environment `renv::init()` and restore the dependencies with
`renv::restore()`: be sure to check that your working directory corresponds to the
root directory of the project, in which the `renv.lock` file is located.

you need to download quarto (<https://quarto.org> in order to render the website 
files each time a new batch of data gets downloaded each day (after running the 
command `quarto render`, all the website files are stored in the _site/ directory)

I'm using nginx (<https://nginx.org/en/download.html>) for a barebones http server,
using certbot for https support.

I'm currently hosting my site on amazon aws, using a EC2 instance with nginx
installed. See <https://quarto.org/docs/publishing/> for easier (albeit more 
confusing with the current set-up) solutions.

All the data is stored in the form of a postgresql database, using a RDS
amazon instance for an easy integration with the aforementioned EC2. For a long 
time I just stored separate files for each day data and then aggregated them into
an R dataframe. You can do both (the former clearly scales better).

create a .Renviron file in your home directory with the environment variables for
accessing the database (`DB_USER`, `DB_HOST`, `DB_NAME`, `DB_PORT`) via R script

in your bash/zsh profile file, add the following lines if you want to receive 
communications about exceptions and executions, when not running locally:
`export TELEGRAM_BOT_TOKEN=<your-token-here>`
`export TELEGRAM_CHAT_ID=<your-chat-id-here>`

Other things to change are the shabangs (!#) for executable files (like in 
script.R), to match the correct path to file on your system of python/R executables. 
You should obviously keep the filesystem structure untampered.
 
