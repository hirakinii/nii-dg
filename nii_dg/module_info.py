#!/usr/bin/env python3
# coding: utf-8

"""
Configuration parameters for the nii_dg package.
"""

GH_OWNER: str = "hirakinii"
"""str: The GitHub repository owner for the nii_dg package."""

GH_REPO_NAME: str = "nii-dg"
"""str: The GitHub repository name for the nii_dg package."""

GH_REPO: str = f"{GH_OWNER}/{GH_REPO_NAME}"
"""str: The GitHub repository path for the nii_dg package."""

GH_REF: str = "demo-myschema-01"
"""str: The GitHub reference (tag or branch) for the nii_dg package."""


if __name__ == "__main__":
    print(GH_REF, end="")
