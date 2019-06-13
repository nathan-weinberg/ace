# ACE - Archived Contact Engine

## Purpose
ACE is a simple text-based CLI program designed to display and manipulate contact data.

### Features

- Search for contacts with specific affiliations
- Create and delete contacts manually, or import data from a CSV or VCF file
- Export your contact data to a CSV or VCF file

## Usage

To run: `$ python3 interface.py`

### Database

Addtionally, a MySQL instance must be running for the app to function correctly. You can setup the database for the first time using the provided `schema.sql` file. You must also have a configuration YAML file. By default the program searches for a file named "config.yaml" (based off "config.yaml.example") in the same directory as "interface.py". If you wish to use a different configuaration filename, you may specify it as a command line argument. Example:

`$ python3 interface.py my_config_file.yaml`

Quickstart for Local Use:

`$ cp config.yaml.example config.yaml`

### Packages

To install packages run:

`$ pip install -r requirements.txt`
