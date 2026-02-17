# Alembic configuration

Since we use SQLAlchemy, we use Alembic for database migrations. This file contains the configuration for Alembic, which is used by the alembic command-line tool to generate and apply migrations.

## Script location

Describes the path to migration scripts.

This is typically a path given in POSIX (e.g. forward slashes) format, relative to the token %(here)s which refers to the location of the .ini file.

## File template

Template used to generate migration file names, the default value is %%(rev)s_%%(slug)s
see https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file
for all available tokens.

### Template examples

    #To prepend the date and time to the file name:
    file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s
    
    #Or organize into date-based subdirectories (requires recursive_version_locations = true)
    file_template = %%(year)d/%%(month).2d/%%(day).2d_%%(hour).2d%%(minute).2d_%%(second).2d_%%(rev)s_%%(slug)s

## Prepend to sys path

The sys.path path will be prepended with the specified path.

Defaults to the current working directory (.). For multiple paths, the path separator is defined by "path_separator".

## Timezone

Timezone to use when rendering the date within the migration file as well as the filename.
If specified, requires the tzdata library.
Leave blank for localtime.

## Truncate slug length

Max length of characters to apply to the "slug" field.

## Revision environment

Set to 'true' to run the environment during the 'revision' command, regardless of autogenerate.

## Sourceless

Set to 'true' to allow .pyc and .pyo files without a source .py file to be detected as revisions in the versions/ directory.

## Version locations

Version location specification; This defaults to <script_location>/versions.
When using multiple version directories, initial revisions must be specified with --version-path.

## Path separator

This indicates what character is used to split lists of file paths, including version_locations and prepend_sys_path within configparser files.

Valid values are:

- :
- ;
- space
- newline
- os (default, uses os.pathsep)

## Recursive version locations

Set to 'true' to search source files recursively in each "version_locations" directory.

## Output encoding

The output encoding used when revision files are written from script.py.mako.

## SQLAlchemy URL

Database URL. This is consumed by the user-maintained env.py script only.

## Post write hooks

Defines scripts or Python functions that are run on newly generated revision scripts.

### Examples

#### Black

    hooks = black
    black.type = console_scripts
    black.entrypoint = black
    black.options = -l 79 REVISION_SCRIPT_FILENAME

#### Ruff

    hooks = ruff
    ruff.type = module
    ruff.module = ruff
    ruff.options = check --fix REVISION_SCRIPT_FILENAME
