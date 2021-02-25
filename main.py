#!/usr/bin/env python
import os
import logging

import arrow
import click
from loguru import logger
import json
import requests


def fetch_ripe(location="/tmp/roa.json"):
    ripe_url = "https://rpki-validator.ripe.net/api/export-extended.json"

    FilePath = location
    if not os.path.isfile(FilePath):
        try:
            response = requests.get(ripe_url)
        except requests.ConnectionError:
            logger.debug("Unable to connect to RIPE")
            return False
        if response.status_code == 200:
            with open(FilePath, "wb") as f:
                f.write(response.content)
    return True


@click.command()
@click.option("--asn", required=True, help="ASN that you want to check")
@click.option(
    "--days", required=True, help="Check ROAs is going to expire in certain days"
)
def main(**kwargs):
    if fetch_ripe():
        rpki_roas = open("/tmp/roa.json").read()
        rpki_json = json.loads(rpki_roas)
        for i in rpki_json["roas"]:
            if arrow.get(
                i["notAfter"]
            ).timestamp - arrow.utcnow().timestamp < 60 * 60 * 24 * int(
                kwargs.get("days")
            ):
                if kwargs.get("asn") == i["asn"]:
                    logger.debug(
                        f"{i['prefix']} is expiring soon. it is invalid after {i['notAfter']}"
                    )


if __name__ == "__main__":
    main()
