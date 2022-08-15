# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## 1.3.2 - 2022-08-15

### Fixed
- make sure checks/notifiers exists in config

## 1.3.1 - 2022-08-15

### Added
- CONFIG, NOTIFIERS, CHECKS can contain yaml string
- CONFIG_FILE, NOTIFIERS_FILE, CHECKS_FILE are pointers to a file

## 1.3.0 - 2022-08-15

### Added
- added support for influxdb v2 notifier
- can specify notifiers (--notifiers) and checks (--checks) are seperate files

### Changed
- config-file options is deprecated in favor for config

## 1.2.2 - 2021-08-13

### Fixed
- error when passing copy of data for filewrite check

## 1.2.1 - 2021-07-26

### Fixed
- error with eventlet and ssl, replaced by downloading 1K chunks and
  checking time spend.

## 1.2.0 - 2021-07-26

### Added
- Random number monitor, given a mark randomly generates a number and
  checks it with the mark.

### Changed
- timeout in download now applies to actual download time, if download
  times out it will be recorded as a failure.
- when download fails, it will still record the download speed.
- if a checks fails and then succeeds, do not send a message if threshold
  is greater than 1.

### Fixed
- if no ssl was given for download, it would throw an exception

## 1.1.0 - 2021-07-19

### Added
- enable download check

## 1.0.1 - 2021-07-19

### Added
- can add tags to slack that will be displayed as fields in the message
- github action to create a new release when pushed to main branch

## 1.0.0 - 2021-07-16

Initial release.

This supports the following checks:
- hostport
- ping
- filewrite

This supports the following notifiers:
- console
- email
- influxdb
- slack
