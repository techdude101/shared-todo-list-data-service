# Shared To-Do List Data Service
This service is responsible for handling to-do list data.

## Quickstart
### Development Environment

#### Docker (recommended)
`docker compose -f compose-dev.yaml up -d`  

#### Local
`pip install -r requirements.txt`  
`python3 -m flask run --debug --reload --host 0.0.0.0 --port 8000`  

### Run Tests
`pip install -r requirements-test.txt`  
`coverage run -m pytest`

*test coverage reports*  
`coverage report`  
`coverage html`

### Lint
`pip install -r requirements-test.txt`  
`flake8 app`  

## Release
*First Release*  
`standard-version --first-release`  

*Dry Run - simulate the release process without making any modifications*  
`standard-version --dry-run`  
