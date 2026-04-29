# Template project

## Use Case

This project is to be used as a project template. It contains all the basic tool configuration files for a project.

## Develop

### Useful Commands When Developing

Open a bash command line inside container using the command:

```
docker-compose run project-dev
```

The bash command line within the docker container allows to run the commands below:

#### Formatting the code

The code can be formatted with:

```
make format
```

#### Checking code formatting

The code formatting can be checked with:

```
make format_check
```

#### Checking the code styling and typing

The code can be checked with:

```
make static
```

#### Running all unit tests

You can run all tests with:

```
make test
```

#### Checking the test coverage

This can be checked with:

```
make test_coverage
```

### CI

You can view the SAST report:
- On your merge request dashboard, by clicking "View full report" in the "Security" area
- In the "semgrep-sast" job of the pipeline, by clicking "Browse" under **Job artifacts** in the right sidebar

You can view the code quality report:
- In the "code_quality" job of the pipeline, by clicking "Browse" under **Job artifacts** in the right sidebar

## Run

How to run an example.

## Modules

The code design and modules.
