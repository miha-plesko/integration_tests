import pytest
from itertools import product

from cfme.configure.settings import DefaultView
from cfme.containers.container import Container
from cfme.containers.provider import ContainersProvider
from cfme.containers.project import Project
from cfme.containers.route import Route
from cfme.containers.node import Node
from cfme.containers.replicator import Replicator
from cfme.web_ui import toolbar as tb
from utils import testgen
from utils.version import current_version
from utils.appliance.implementations.ui import navigate_to

pytestmark = [
    pytest.mark.uncollectif(
        lambda: current_version() < "5.6"),
    pytest.mark.usefixtures('setup_provider'),
    pytest.mark.tier(1)]
pytest_generate_tests = testgen.generate(
    testgen.container_providers, scope='function')

VIEWS = ['Grid View', 'Tile View', 'List View']

mapping = {
    'Containers Providers': ContainersProvider,
    'Projects': Project,
    'Routes': Route,
    'Nodes': Node,
    'Containers': Container,
    'Replicators': Replicator
}


# CMP-9936 # CMP-9937 # CMP-9938 # CMP-10000 # CMP-10001 # CMP-10003

@pytest.mark.parametrize(('button_group', 'view'), product(mapping.keys(), VIEWS))
def test_containers_providers_default_view(button_group, view):
    """ Containers Providers/Projects/Routes/Nodes/Containers/Replicators default view test
        This test checks successful change of default views settings for Containers -->
        Providers/Projects/Routes/Nodes/Containers/Replicators menu
        Steps:
            * Goes to Settings --> My Settings --> Default Views menu and change the default view
             settings of Containers --> Containers Providers/Projects/Routes/Nodes
             /Containers/Replicators
              to Grid/Tile/List view
            * Goes to Compute --> Containers --> Providers and verifies the selected view
        """
    DefaultView.set_default_view(button_group_name=button_group, default=view)
    navigate_to(mapping[button_group], 'All', use_resetter=False)
    assert tb.is_active(view), "{}'s {} setting failed".format(view, button_group)
