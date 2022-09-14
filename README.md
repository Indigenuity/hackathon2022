# S3Zero -- Hackathon 2022 Project

See [Confluence](https://cyence.atlassian.net/wiki/spaces/ADS/pages/2493874447/S3Zero) for presentation

To run the main script, you need permission to an S3 bucket.  Change `s3zero.py` to reflect your AWS profile settings.  Once you've done that:

```shell
poetry install
poetry run ./s3zero.py write <yourfile>
poetry run ./s3zero.py read ./out/<yourfile>
```