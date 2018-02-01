# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "microfinance"
app_title = "Microfinance"
app_publisher = "Libermatic"
app_description = "Microfinance management"
app_icon = "fa fa-university"
app_color = "#8BC34A"
app_email = "info@libermatic.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "assets/css/microfinance.css"
# app_include_css = "assets/microfinance/css/devel.css"
app_include_js = ["assets/js/microfinance.js", "assets/microfinance/js/utils.js"]

# include js, css files in header of web template
# web_include_css = "/assets/microfinance/css/microfinance.css"
# web_include_js = "/assets/microfinance/js/microfinance.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
        'Customer' : ["public/js/customer_details.js"],
    }
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "microfinance.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "microfinance.install.before_install"
after_install = "microfinance.setup.after_install"
setup_wizard_complete = "microfinance.setup.after_wizard_complete"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "microfinance.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"microfinance.tasks.all"
# 	],
	"daily": [
		"microfinance.tasks.daily"
	],
# 	"hourly": [
# 		"microfinance.tasks.hourly"
# 	],
# 	"weekly": [
# 		"microfinance.tasks.weekly"
# 	]
# 	"monthly": [
# 		"microfinance.tasks.monthly"
# 	]
}

# Testing
# -------

# before_tests = "microfinance.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "microfinance.event.get_events"
# }
