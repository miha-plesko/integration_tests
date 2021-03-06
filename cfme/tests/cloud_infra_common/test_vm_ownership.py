import fauxfactory
import pytest

import cfme.configure.access_control as ac
from cfme import test_requirements
from cfme.base.credential import Credential
from cfme.common.provider import BaseProvider
from cfme.common.vm import VM
from cfme.exceptions import VmOrInstanceNotFound
from cfme.utils.blockers import BZ


pytestmark = [
    test_requirements.ownership,
    pytest.mark.meta(blockers=[BZ(1380781, forced_streams=["5.7"])]),
    pytest.mark.tier(3),
    pytest.mark.provider([BaseProvider], required_fields=['ownership_vm'], scope='module')
]


@pytest.yield_fixture(scope="module")
def role_only_user_owned(appliance):
    appliance.server.login_admin()
    role = appliance.collections.roles.create(
        name='role_only_user_owned_' + fauxfactory.gen_alphanumeric(),
        vm_restriction='Only User Owned'
    )
    yield role
    appliance.server.login_admin()
    role.delete()


@pytest.yield_fixture(scope="module")
def group_only_user_owned(appliance, role_only_user_owned):
    group_collection = appliance.collections.groups
    group = group_collection.create(
        description='group_only_user_owned_{}'.format(fauxfactory.gen_alphanumeric()),
        role=role_only_user_owned.name)
    yield group
    appliance.server.login_admin()
    group.delete()


@pytest.yield_fixture(scope="module")
def role_user_or_group_owned(appliance):
    appliance.server.login_admin()
    role = appliance.collections.roles.create(
        name='role_user_or_group_owned_' + fauxfactory.gen_alphanumeric(),
        vm_restriction='Only User or Group Owned'
    )
    yield role
    appliance.server.login_admin()
    role.delete()


@pytest.yield_fixture(scope="module")
def group_user_or_group_owned(appliance, role_user_or_group_owned):
    group_collection = appliance.collections.groups
    group = group_collection.create(
        description='group_user_or_group_owned_{}'.format(fauxfactory.gen_alphanumeric()),
        role=role_user_or_group_owned.name)
    yield group
    appliance.server.login_admin()
    group.delete()


def new_credential():
    # BZ1487199 - CFME allows usernames with uppercase chars which blocks logins
    if BZ.bugzilla.get_bug(1487199).is_opened:
        return Credential(principal='uid' + fauxfactory.gen_alphanumeric().lower(), secret='redhat')
    else:
        return Credential(principal='uid' + fauxfactory.gen_alphanumeric(), secret='redhat')


@pytest.yield_fixture(scope="module")
def user1(appliance, group_only_user_owned):
    user1 = new_user(appliance, group_only_user_owned)
    yield user1
    appliance.server.login_admin()
    user1.delete()


@pytest.yield_fixture(scope="module")
def user2(appliance, group_only_user_owned):
    user2 = new_user(appliance, group_only_user_owned)
    yield user2
    appliance.server.login_admin()
    user2.delete()


@pytest.yield_fixture(scope="module")
def user3(appliance, group_user_or_group_owned):
    user3 = new_user(appliance, group_user_or_group_owned)
    yield user3
    appliance.server.login_admin()
    user3.delete()


def new_user(appliance, group_only_user_owned):
    user = appliance.collections.users.create(
        name='user_' + fauxfactory.gen_alphanumeric(),
        credential=new_credential(),
        email='abc@redhat.com',
        group=group_only_user_owned,
        cost_center='Workload',
        value_assign='Database'
    )
    return user


def check_vm_exists(vm_ownership):
    """ Checks if VM exists through All Instances tab.

    Args:
        vm_ownership: VM object for ownership test

    Returns:
        :py:class:`bool`
    """
    try:
        vm_ownership.find_quadicon(from_any_provider=True)
        return True
    except VmOrInstanceNotFound:
        return False


def test_form_button_validation(request, user1, setup_provider, provider):
    ownership_vm = provider.data['ownership_vm']
    user_ownership_vm = VM.factory(ownership_vm, provider)
    # Reset button test
    user_ownership_vm.set_ownership(user=user1.name, click_reset=True)
    # Cancel button test
    user_ownership_vm.set_ownership(user=user1.name, click_cancel=True)
    # Save button test
    user_ownership_vm.set_ownership(user=user1.name)
    # Unset the ownership
    user_ownership_vm.unset_ownership()


def test_user_ownership_crud(request, user1, setup_provider, provider):
    ownership_vm = provider.data['ownership_vm']
    user_ownership_vm = VM.factory(ownership_vm, provider)
    # Set the ownership and checking it
    user_ownership_vm.set_ownership(user=user1.name)
    with user1:
        assert user_ownership_vm.exists, "vm not found"
    user_ownership_vm.unset_ownership()
    with user1:
        assert not check_vm_exists(user_ownership_vm), "vm exists! but shouldn't exist"


def test_group_ownership_on_user_only_role(request, user2, setup_provider, provider):
    ownership_vm = provider.data['ownership_vm']
    group_ownership_vm = VM.factory(ownership_vm, provider)
    group_ownership_vm.set_ownership(group=user2.group.description)
    with user2:
        assert not check_vm_exists(group_ownership_vm), "vm exists! but shouldn't exist"
    group_ownership_vm.set_ownership(user=user2.name)
    with user2:
        assert group_ownership_vm.exists, "vm exists"


def test_group_ownership_on_user_or_group_role(
        request, user3, setup_provider, provider):
    ownership_vm = provider.data['ownership_vm']
    group_ownership_vm = VM.factory(ownership_vm, provider)
    group_ownership_vm.set_ownership(group=user3.group.description)
    with user3:
        assert group_ownership_vm.exists, "vm not found"
    group_ownership_vm.unset_ownership()
    with user3:
        assert not check_vm_exists(group_ownership_vm), "vm exists! but shouldn't exist"


# @pytest.mark.meta(blockers=[1202947])
# def test_ownership_transfer(request, user1, user3, setup_infra_provider):
#    user_ownership_vm = VM.factory('cu-9-5', setup_infra_provider)
#    user_ownership_vm.set_ownership(user=user1.name)
#    with user1:
#        # Checking before and after the ownership transfer
#        assert user_ownership_vm.exists, "vm not found"
#        user_ownership_vm.set_ownership(user=user3.name)
#        assert not user_ownership_vm.exists, "vm exists"
#    with user3:
#        assert user_ownership_vm.exists, "vm not found"
#    user_ownership_vm.unset_ownership()
#    with user3:
#        assert set_ownership_to_user.exists, "vm exists"
