# TurboQuant CPU Research

## Use Case

This directory contains TurboQuant CPU research notes, benchmark scripts, plots,
and raw results. The main implementation lives in the repository-level
`llama.cpp/` snapshot.

## Develop

### Useful Commands When Developing

Open a bash command line inside container using the command:

```
docker-compose run turboquant-dev
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

## Run

Benchmark and quality-evaluation scripts are in `autoresearch/`. They assume the
modified `llama.cpp` binaries have been built and that the referenced GGUF model
files exist locally or on the configured worker.

## Modules

- `autoresearch/` - benchmark, plotting, and quality-analysis utilities.
- `results/` - captured benchmark outputs and generated plots.
- `results/source_code/` - source snapshots and patch artifacts from the kernel
  audit.
