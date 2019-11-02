![AppVeyor](https://img.shields.io/appveyor/ci/takitsu21/twitter-bot) [![python versions](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue)](https://www.python.org/) [![GitHub](https://img.shields.io/github/license/takitsu21/twitter-bot)](LICENCE)

# twitter-bot

twitter-bot is a bot that RT and follow according to a pattern to win prizes.

## Getting started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Dependencies

* [Python 3.6/3.7/3.8](https://www.python.org/)

### Prerequisites

```
git clone https://github.com/takitsu21/twitter-bot
```

#### Follow the steps
* Goto [Twitter apps](https://developer.twitter.com/en/apps)
* Create an app
* Rename `.env.example` to `.env`
* Fill out the `.env` file with your Consumer API keys and Access token

### Installing

```
make install
```
OR
```
python -m pip install -r requirements
```

### Running

```
make run
```
OR
```
python app.py
```

Follow the instructions.

### Built with

* [tweepy](https://github.com/tweepy/tweepy) - API used for twitter
* [console-menu](https://github.com/aegirhall/console-menu) - Shell interface
* [python-decouple](https://github.com/henriquebastos/python-decouple) - Config file
* [colorama](https://github.com/tartley/colorama) - Eye care

### Contributing

Everyone can contribute, just make a pull requests.

### License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details