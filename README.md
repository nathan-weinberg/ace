# ACE - Archived Contact Engine
![flake8](https://github.com/nathan-weinberg/ace/workflows/flake8/badge.svg)

## Purpose
ACE is a text-based CLI program designed to display and manipulate contact data. It aims to provide a simple but intutive interface combined with precision relational database control.

### Features
- Search for contacts with specific affiliations
- Create and delete contacts manually, or import data from a CSV or VCF file
- Export your contact data to a CSV or VCF file

## Usage
To run: `$ ./interface.py`

### Database
A MySQL instance must be running for the app to function correctly. You can setup the database for the first time using the provided `schema.sql` file. 

### Configuration
You must have a configuration YAML file present filled with credentials to connect to the MySQL database instance. By default the program searches for a file named "config.yaml" (based off "config.yaml.example") in the same directory as "interface.py". If you wish to use a different configuaration filename, you may specify it as a command line argument. Example:

`$ ./interface.py --config my_config_file.yaml`

Quickstart for Local Use:

`$ cp config.yaml.example config.yaml`

#### Using a Test Database
If you wish to use a test database, you can specify the credentials in your config file under a section defined as "mysql_test" (see "config.yaml.example" for an example) and use it by adding a `--test` flag. Example:

`$ ./interface.py --test`

#### Using a Remote Database
If you intend to use a database instance not running on localhost, ensure you've allowed TCP/IP connections (port 3306) through your firewall, and have a valid database user with proper permissions created for your client host's IP address. You may also need to edit the `mysqld` settings wherever your mysql daemon is running. For more details see [here](https://www.cyberciti.biz/tips/how-do-i-enable-remote-access-to-mysql-database-server.html).

### Packages

To install packages run:

`$ pip install -r requirements.txt`
