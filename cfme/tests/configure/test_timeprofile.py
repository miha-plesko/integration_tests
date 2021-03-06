# -*- coding: utf-8 -*-
import fauxfactory
import pytest

import cfme.configure.settings as st
from cfme import test_requirements
from cfme.configure.settings import TimeProfileAddFormView
from cfme.utils.update import update

pytestmark = [pytest.mark.tier(3),
              test_requirements.settings]


def new_timeprofile():
    return st.Timeprofile(description='time_profile' + fauxfactory.gen_alphanumeric(),
                          scope='Current User',
                          days=True,
                          hours=True,
                          timezone="(GMT-10:00) Hawaii")


@pytest.mark.sauce
def test_timeprofile_crud():
    timeprofile = new_timeprofile()
    timeprofile.create()
    with update(timeprofile):
        timeprofile.scope = 'All Users'
    copied_timeprofile = timeprofile.copy()
    copied_timeprofile.delete()
    timeprofile.delete()


@pytest.mark.sauce
def test_timeprofile_name_max_character_validation():
    tp = st.Timeprofile(
        description=fauxfactory.gen_alphanumeric(50),
        scope='Current User',
        timezone="(GMT-10:00) Hawaii")
    tp.create()
    tp.delete()


@pytest.mark.sauce
def test_days_required_error_validation(soft_assert, appliance):
    tp = st.Timeprofile(
        description='time_profile' + fauxfactory.gen_alphanumeric(),
        scope='Current User',
        timezone="(GMT-10:00) Hawaii",
        days=False,
        hours=True)
    tp.create(cancel=True)
    view = appliance.browser.create_view(TimeProfileAddFormView)
    soft_assert(view.timeprofile_form.help_block.text == "At least one day needs to be selected")
    soft_assert(view.timeprofile_form.save_button.disabled)
    view.timeprofile_form.cancel_button.click()


@pytest.mark.sauce
def test_hours_required_error_validation(soft_assert, appliance):
    tp = st.Timeprofile(
        description='time_profile' + fauxfactory.gen_alphanumeric(),
        scope='Current User',
        timezone="(GMT-10:00) Hawaii",
        days=True,
        hours=False)
    tp.create(cancel=True)
    view = appliance.browser.create_view(TimeProfileAddFormView)
    soft_assert(view.timeprofile_form.help_block.text == "At least one hour needs to be selected")
    soft_assert(view.timeprofile_form.save_button.disabled)
    view.timeprofile_form.cancel_button.click()


@pytest.mark.sauce
def test_timeprofile_description_required_error_validation(soft_assert, appliance):
    tp = st.Timeprofile(
        description=None,
        scope='Current User',
        timezone="(GMT-10:00) Hawaii")
    tp.create(cancel=True)
    view = appliance.browser.create_view(TimeProfileAddFormView)
    soft_assert(view.timeprofile_form.description.help_block == "Required")
    soft_assert(view.timeprofile_form.save_button.disabled)
    view.timeprofile_form.cancel_button.click()
