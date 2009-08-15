# Makefile for libmagic
SHELL := /bin/bash

# Internal variables.
file_version=0.1.0
root_dir=.
src_dir=${root_dir}/libmagic

# orchestrator targets

prepare_build: clean

test: unit func

all: prepare_build compile test

run_unit: prepare_build compile unit
run_functional: prepare_build compile func

clean:
	@rm -rf .coverage

# action targets

compile:
	@echo "Compiling source code..."
	@rm -f ${compile_log_file} >> /dev/null
	@rm -f -r ${src_dir}/*.pyc >> /dev/null
	@python -m compileall ${src_dir}

unit: compile
	@echo "Running unit tests..."
	@nosetests -d -s --verbose --with-coverage --cover-erase --cover-package=libmagic tests/unit

func: compile
	@echo "Running functional tests..."
	@nosetests -d -s --verbose --with-coverage --cover-erase --cover-package=libmagic tests/functional


