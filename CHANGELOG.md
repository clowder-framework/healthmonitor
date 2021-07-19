# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

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
