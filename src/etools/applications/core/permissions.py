import codecs
import csv

from django.conf import settings
from django.core.cache import cache

from etools.libraries.pythonlib.collections import Vividict


def process_permissions(permission_dict):
    """
    :param permission_dict: the csv file read as a generator of dictionaries
     where the header contains the following keys:

    'Group' - the Django Group the user should belong to - field may be blank.
    'Condition' - the condition that should be required to satisfy.
    'Status' - the status of the model (represents state)
    'Field' - the field we are targetting (eg: start_date) this needs to be spelled exactly as it is on the model
    'Action' - One of the following values: 'view', 'edit', 'required'
    'Allowed' - the boolean 'TRUE' or 'FALSE' if the action should be allowed if the: group match, status match and
    condition match are all valid

    *** note that in order for the system to know what the default behaviour should be on a specified field for a
    specific action, only the conditions opposite to the default should be defined.

    :return:
     a nested dictionary where the first key is the field targeted, the following nested key is the action possible,
     and the last nested key is the action parameter
     eg:
     {'start_date': {'edit': {'false': [{'condition': 'condition2',
                                         'group': 'UNICEF USER',
                                         'status': 'Active'}]},
                     'required': {'true': [{'condition': '',
                                            'group': 'UNICEF USER',
                                            'status': 'Active'},
                                           {'condition': '',
                                            'group': 'UNICEF USER',
                                            'status': 'Signed'}]},
                     'view': {'true': [{'condition': 'condition1',
                                        'group': 'PM',
                                        'status': 'Active'}]}}}
    """

    result = Vividict()
    possible_actions = ['edit', 'required', 'view']

    for row in permission_dict:
        field = row['Field Name']
        action = row['Action'].lower()
        allowed = row['Allowed'].lower()
        assert action in possible_actions

        if isinstance(result[field][action][allowed], dict):
            result[field][action][allowed] = []

        # this action should not have been defined with any other allowed param
        assert list(result[field][action].keys()) == [allowed], \
            'There cannot be two types of "allowed" defined on the same ' \
            'field with the same action as the system will not be able' \
            ' to have a default behaviour.  field=%r, action=%r, allowed=%r' \
            % (field, action, allowed)

        result[field][action][allowed].append({
            'group': row['Group'],
            'condition': row['Condition'],
            'status': row['Status'].lower()
        })
    return result


def import_permissions(model_name):
    permission_file_map = {
        'Intervention': settings.PACKAGE_ROOT + '/applications/partners/permission_matrix/intervention_permissions.csv',
        'Agreement': settings.PACKAGE_ROOT + '/applications/partners/permission_matrix/agreement_permissions.csv'
    }

    def process_file():
        with codecs.open(permission_file_map[model_name], 'r', encoding='ascii') as csvfile:
            sheet = csv.DictReader(csvfile, delimiter=',', quotechar='|')
            result = process_permissions(sheet)
        return result

    cache_key = "public-{}-permissions".format(model_name.lower())
    response = cache.get_or_set(cache_key, process_file, 60 * 60 * 24)

    return response
