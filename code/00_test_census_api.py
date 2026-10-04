"""Check that a working Census API key is available before running the
download scripts that depend on one (e.g. code/02_download_data.py).

Looks for CENSUS_API_KEY first as a pre-existing environment variable
(shell profile, direnv, etc.), then falls back to a .env file in the
repository root (see .env.example). Either way, makes a small live request
to api.census.gov to confirm the key actually works, since a key can be
present but invalid, revoked, or mistyped.

Run from the repository root: python code/00_test_census_api.py
"""

import os

import requests
from dotenv import load_dotenv

TEST_URL = "https://api.census.gov/data/2023/acs/acs5"
TEST_PARAMS = {"get": "NAME", "for": "state:06"}  # California; cheap, stable query
KEY_SIGNUP_URL = "https://api.census.gov/data/key_signup.html"


def find_api_key():
    pre_existing = os.environ.get("CENSUS_API_KEY")
    if pre_existing:
        return pre_existing, "pre-existing environment variable"

    load_dotenv()
    from_dotenv = os.environ.get("CENSUS_API_KEY")
    if from_dotenv:
        return from_dotenv, ".env file"

    return None, None


def check_api_key(key):
    # An invalid key doesn't get a 4xx response: the Census API redirects
    # (still HTTP 200) to an HTML "invalid key" page instead of returning
    # the requested JSON, so success must be judged by the body, not the
    # status code.
    response = requests.get(TEST_URL, params={**TEST_PARAMS, "key": key})
    if response.status_code != 200:
        return False, response.text
    try:
        response.json()
    except ValueError:
        return False, f"Expected JSON, got HTML (redirected to {response.url})"
    return True, None


def main():
    key, source = find_api_key()
    if key is None:
        print(
            "FAILED: No CENSUS_API_KEY found in the environment or a .env file.\n"
            f"Get a free key at {KEY_SIGNUP_URL}, then either export it as "
            "CENSUS_API_KEY in your shell/direnv, or copy .env.example to .env "
            "and fill it in."
        )
        raise SystemExit(1)

    ok, detail = check_api_key(key)
    if not ok:
        print(
            f"FAILED: Found CENSUS_API_KEY ({source}), but the Census API "
            f"rejected it:\n{detail}\n"
            f"Double check the key, or request a new one at {KEY_SIGNUP_URL}."
        )
        raise SystemExit(1)

    print(f"OK: CENSUS_API_KEY ({source}) works, Census API responded successfully.")


if __name__ == "__main__":
    main()
