# Introduction
This is the crawler and API backend for the Tao Network.

This is alpha software. Use at your own risk.

# Requirements
- Python 3
- Redis
- Postgres
- RabbitMQ

Docker packages are preferred for development environments.  Development is intended to be performed within a python virtual environment (virtualenv or similar) accessing docker packages which run the other required software. A docker-compose.yml is provided for convenience.

# Configuration
Settings for communicating with related docker images can be found in ming/settings.py.

Make sure to set your Postgres password in docker-compose.yml and set it accordingly in ming/settings.py!

# Running

```
docker-compose up
```

Celery is used to fork worker processes to import blockchain data each block.  This includes tokens (TRC20, TRC21, TRC721), smart contracts, and governance data.

RabbitMQ management is exposed on port 8080. Remove this mapping to obscure it.

The docker-compose configuration is intended for development ONLY! Do not use in production!

# Notes
In a production environment multiple workers are used in order to crawl the entire chain from block 0 in a timely manner.  After the initial crawl only a single worker is required to keep the chain current, however multiple workers provides redundancy.

REMEMBER: each time you change the code you must run
'''
docker-compose build
'''
