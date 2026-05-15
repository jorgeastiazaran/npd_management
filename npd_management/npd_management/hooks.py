# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "npd_management"
app_title = "NPD Management"
app_publisher = "Jorge"
app_description = "NPD Management App for Tecnofood"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "tecnofoodmx@gmail.com"
app_license = "MIT"

# ─── Fixtures ────────────────────────────────────────────────────────────────
# These records are exported to npd_management/fixtures/ and auto-imported
# on `bench migrate` and `bench install-app`. This ensures Client Scripts,
# Naming Series, and any other config travels with the app to production.
fixtures = [
    {
        "dt": "Property Setter",
        "filters": [["doc_type", "like", "NPD%"]]
    },
]

# ─── Hooks ───────────────────────────────────────────────────────────────────
# after_migrate: runs after every `bench migrate`
after_migrate = "npd_management.setup.install.after_install"

# after_install: runs once when the app is first installed on a new site
after_install = "npd_management.setup.install.after_install"

doc_events = {
    "Item": {
        # "after_insert": "npd_management.api.npd_utils.link_promoted_item"
    }
}
