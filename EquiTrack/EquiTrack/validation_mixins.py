from __future__ import unicode_literals
import copy
import logging
from django.apps import apps
from django.db.models import ObjectDoesNotExist
from django.utils.functional import cached_property

from django_fsm import (
    can_proceed, has_transition_perm,
    get_all_FIELD_transitions
)

from rest_framework.exceptions import ValidationError

from EquiTrack.stream_feed.actions import create_snapshot_activity_stream
from EquiTrack.parsers import parse_multipart_data


def check_editable_fields(obj, fields):
    if not getattr(obj, 'old_instance', None):
        return False, fields
    for field in fields:
        old_instance = obj.old_instance
        if getattr(obj, field) != getattr(old_instance, field):
            return False, field
    return True, None


def check_required_fields(obj, fields):
    for f_name in fields:
        field = getattr(obj, f_name)
        try:
            response = field.all().count() > 0
        except AttributeError:
            response = field is not None
        if response is False:
            return False, f_name

    return True, None


def check_rigid_related(obj, related):
    current_related = list(getattr(obj, related).all())
    old_related = list(getattr(obj.old_instance, '{}_old'.format(related), []))
    if len(current_related) != len(old_related):
        return False
    if len(current_related) == 0:
        return True

    field_names = current_related[0]._meta.get_all_field_names()
    current_related.sort(key=lambda x: x.id)
    old_related.sort(key=lambda x: x.id)
    comparison_map = zip(current_related, old_related)
    # check if any field on the related model was changed
    for i in comparison_map:
        for field in field_names:
            if getattr(i[0], field) != getattr(i[1], field):
                return False
    return True


def check_rigid_fields(obj, fields, old_instance=None, related=False):
    if not old_instance and not getattr(obj, 'old_instance', None):
        return False, None
    for f_name in fields:
        old_instance = old_instance or obj.old_instance
        new_field = getattr(obj, f_name)
        old_field = getattr(old_instance, f_name)
        if hasattr(new_field, 'all'):
            # this could be a related field, unfortunately i can't figure out a isinstance check
            if related:
                if not check_rigid_related(obj, f_name):
                    return False, f_name

        elif new_field != old_field:
                return False, f_name

    return True, None


class ValidatorViewMixin(object):

    def _parse_data(self, request):
        dt_cp = request.data
        for k in dt_cp:
            if dt_cp[k] in ['', 'null']:
                dt_cp[k] = None
            elif dt_cp[k] == 'true':
                dt_cp[k] = True
            elif dt_cp[k] == 'false':
                dt_cp[k] = False

        dt = parse_multipart_data(dt_cp)
        return dt

    def up_related_field(self, mother_obj, field, fieldClass, fieldSerializer, rel_prop_name, reverse_name,
                         partial=False, nested_related_names=None):
        if not field:
            return

        if isinstance(field, list):
            for item in field:
                item.update({reverse_name: mother_obj.pk})
                nested_related_data = {}
                if nested_related_names:
                    nested_related_data = {k: v for k, v in item.items() if k in nested_related_names}
                if item.get('id', None):
                    try:
                        instance = fieldClass.objects.get(id=item['id'])
                    except fieldClass.DoesNotExist:
                        instance = None

                    instance_serializer = fieldSerializer(instance=instance,
                                                          data=item,
                                                          partial=partial,
                                                          context=nested_related_data)
                else:
                    instance_serializer = fieldSerializer(data=item,
                                                          context=nested_related_data)

                try:
                    instance_serializer.is_valid(raise_exception=True)
                    # ValidationError can be raised by one of the sub-related fields inside the serializer on save
                    instance_serializer.save()
                except ValidationError as e:
                    e.detail = {rel_prop_name: e.detail}
                    raise e
        else:
            # This is in case we have a OneToOne field
            field.update({reverse_name: mother_obj.pk})
            nested_related_data = {}
            if nested_related_names:
                nested_related_data = {k: v for k, v in field.items() if k in nested_related_names}
            if field.get('id', None):
                try:
                    instance = fieldClass.objects.get(id=field['id'])
                except fieldClass.DoesNotExist:
                    instance = None

                instance_serializer = fieldSerializer(instance=instance,
                                                      data=field,
                                                      partial=partial,
                                                      context=nested_related_data)
            else:
                instance_serializer = fieldSerializer(data=field,
                                                      context=nested_related_data)

            try:
                instance_serializer.is_valid(raise_exception=True)
                # ValidationError can be raised by one of the sub-related fields inside the serializer on save
                instance_serializer.save()
            except ValidationError as e:
                e.detail = {rel_prop_name: e.detail}
                raise e

    def my_create(self, request, related_f, snapshot=None, nested_related_names=None, **kwargs):
        my_relations = {}
        partial = kwargs.pop('partial', False)
        data = self._parse_data(request)

        for f in related_f:
            my_relations[f] = data.pop(f, [])

        main_serializer = self.get_serializer(data=data)
        main_serializer.context['skip_global_validator'] = True
        main_serializer.is_valid(raise_exception=True)

        main_object = main_serializer.save()

        if snapshot:
            create_snapshot_activity_stream(request.user, main_object, created=True)

        def _get_model_for_field(field):
            return main_object.__class__._meta.get_field(field).related_model

        def _get_reverse_for_field(field):
            return main_object.__class__._meta.get_field(field).remote_field.name
        for k, v in my_relations.iteritems():
            self.up_related_field(main_object, v, _get_model_for_field(k), self.SERIALIZER_MAP[k],
                                  k, _get_reverse_for_field(k), partial, nested_related_names)

        return main_serializer

    def my_update(self, request, related_f, snapshot=None, nested_related_names=None, **kwargs):
        partial = kwargs.pop('partial', False)
        data = self._parse_data(request)

        my_relations = {}
        for f in related_f:
            my_relations[f] = data.pop(f, [])

        old_instance = self.get_object()
        instance = self.get_object()
        main_serializer = self.get_serializer(instance, data=data, partial=partial)
        main_serializer.context['skip_global_validator'] = True
        main_serializer.is_valid(raise_exception=True)

        if snapshot:
            create_snapshot_activity_stream(request.user, main_serializer.instance, delta_dict=data)

        main_object = main_serializer.save()

        for k in my_relations.iterkeys():
            try:
                rel_field_val = getattr(old_instance, k)
            except ObjectDoesNotExist:
                pass
            else:
                prop = '{}_old'.format(k)

                try:
                    val = list(rel_field_val.all())
                except AttributeError:
                    # This means OneToOne field
                    val = rel_field_val

                setattr(old_instance, prop, val)

        def _get_model_for_field(field):
            return main_object.__class__._meta.get_field(field).related_model

        def _get_reverse_for_field(field):
            return main_object.__class__._meta.get_field(field).remote_field.name

        for k, v in my_relations.iteritems():
            self.up_related_field(main_object, v, _get_model_for_field(k), self.SERIALIZER_MAP[k],
                                  k, _get_reverse_for_field(k), partial, nested_related_names)

        return instance, old_instance, main_serializer


class TransitionError(BaseException):
    def __init__(self, message=[]):
        if not isinstance(message, list):
            raise TypeError('Transition exception takes a list of errors not %s' % type(message))
        super(TransitionError, self).__init__(message)


class StateValidError(BaseException):
    def __init__(self, message=[]):
        if not isinstance(message, list):
            raise TypeError('Transition exception takes a list of errors not %s' % type(message))
        super(StateValidError, self).__init__(message)

class BasicValidationError(BaseException):
    def __init__(self, message=''):
        super(BasicValidationError, self).__init__(message)

def error_string(function):
    def wrapper(*args, **kwargs):
        try:
            valid = function(*args, **kwargs)
        except BasicValidationError as e:
            return (False, [e.message])
        else:
            if valid and type(valid) is bool:
                return (True, [])
            else:
                return (False, [function.__name__])
    return wrapper


def transition_error_string(function):
    def wrapper(*args, **kwargs):
        try:
            valid = function(*args, **kwargs)
        except TransitionError as e:
            return (False, e.message)

        if valid and type(valid) is bool:
            return (True, [])
        else:
            return (False, ['generic_transition_fail'])
    return wrapper

def state_error_string(function):
    def wrapper(*args, **kwargs):
        try:
            valid = function(*args, **kwargs)
        except StateValidError as e:
            return (False, e.message)

        if valid and type(valid) is bool:
            return (True, [])
        else:
            return (False, ['generic_state_validation_fail'])
    return wrapper

def update_object(obj, kwdict):
    for k, v in kwdict.iteritems():
        setattr(obj, k, v)

class CompleteValidation(object):
    PERMISSIONS_CLASS = None
    def __init__(self, new, user=None, old=None, instance_class=None, stateless=False):
        if old and isinstance(old, dict):
            raise TypeError('if old is transmitted to complete validation it needs to be a model instance')

        if isinstance(new, dict):
            logging.debug('instance is dict')
            logging.debug(old)
            if not old and not instance_class:
                try:
                    instance_class = apps.get_model(getattr(self, 'VALIDATION_CLASS'))
                except LookupError:
                    raise TypeError('Object Transimitted for validation cannot be dict if instance_class is not defined')
            new_id = new.get('id', None) or new.get('pk', None)
            if new_id:
                logging.debug('newid')
                # let it raise the error if it does not exist
                old_instance = old if old and old.id == new_id else instance_class.objects.get(id=new_id)
                new_instance = instance_class.objects.get(id=new_id)
                update_object(new_instance, new)

            else:
                logging.debug('no id')
                old_instance = old
                # TODO: instance_class(**new) can't be called like that if models have m2m fields
                # Workaround for now is not to call the validator from the serializer on new instances
                new_instance = copy.deepcopy(old) if old else instance_class(**new)
                if old:
                    update_object(new_instance, new)
            new = new_instance
            old = old_instance

        self.stateless = stateless
        self.new = new
        if not self.stateless:
            self.new_status = self.new.status
        self.skip_transition = not old
        self.skip_permissions = not user
        self.old = old
        if not self.stateless:
            self.old_status = self.old.status if self.old else None
        self.user = user

        # permissions to be set in each function that is needed, this attribute can change values as auto-update goes through
        # different statuses
        self.permissions = None

    def get_permissions(self, instance):
        if self.PERMISSIONS_CLASS:
            p = self.PERMISSIONS_CLASS(
                user=self.user,
                instance=instance,
                permission_structure=self.new.permission_structure(),
                inbound_check=True)
            return p.get_permissions()
        return None

    def check_transition_conditions(self, transition):
        if not transition:
            return True
        return can_proceed(transition)

    def check_transition_permission(self, transition):
        if not transition:
            return True
        return has_transition_perm(transition, self.user)

    @cached_property
    def transition(self):
        return self._get_fsm_defined_transitions(self.old_status, self.new_status)

    @transition_error_string
    def transitional_validation(self):
        # set old status to get proper transitions
        self.new.status = self.old.status

        # set old instance on instance to make it available to the validation functions
        setattr(self.new, 'old_instance', self.old)
        self.permissions = self.get_permissions(self.new)


        # check conditions and permissions
        conditions_check = self.check_transition_conditions(self.transition)

        if self.skip_permissions:
            permissions_check = True
        else:
            permissions_check = self.check_transition_permission(self.transition)

        # cleanup
        delattr(self.new, 'old_instance')
        self.permissions = None
        self.new.status = self.new_status
        return conditions_check and permissions_check

    @state_error_string
    def state_valid(self):
        if not self.basic_validation[0]:
            return self.basic_validation

        result = True
        # set old instance on instance to make it available to the validation functions
        setattr(self.new, 'old_instance', self.old)
        self.permissions = self.get_permissions(self.new)

        funct_name = "state_{}_valid".format(self.new_status)
        logging.debug('in state_valid finding function: {}'.format(funct_name))
        function = getattr(self, funct_name, None)
        if function:
            result = function(self.new, user=self.user)

        # cleanup
        delattr(self.new, 'old_instance')
        self.permissions = None
        logging.debug('result is: {}'.format(result))
        return result

    def _get_fsm_defined_transitions(self, source, target):
        all_transitions = get_all_FIELD_transitions(self.new, self.new.__class__._meta.get_field('status'))
        for transition in all_transitions:
            if transition.source == source and target in transition.target:
                return getattr(self.new, transition.method.__name__)

    @transition_error_string
    def auto_transition_validation(self, potential_transition):
        logging.debug('in auto transition validation %s' % potential_transition)

        result = self.check_transition_conditions(potential_transition)
        logging.debug("check_transition_conditions returned: {}".format(result))
        return result

    def _first_available_auto_transition(self):
        potential = getattr(self.new.__class__, 'POTENTIAL_AUTO_TRANSITIONS', {})

        # make sure that all potential transitions were labeled correctly and filter out what wasn't
        def filter_tl(potential_transition_list, choices):
            if not potential_transition_list:
                return None

            def my_filter(obj):
                # object should only have one key and should be in the list of choices
                key = next(obj.iterkeys())
                return key in choices
            return filter(lambda obj: my_filter(obj), potential_transition_list)

        # Transition list: list of objects [{'transition_to_status': [auto_changes_function1, auto_changes_function2]}]
        # Represents potential transitions from the current status:
        tl = filter_tl(potential.get(self.new.status, None),
                       [s[0] for s in self.new.__class__._meta.get_field('status').choices])

        logging.debug("Potential transition from the current status: {} -> {}".format(self.new.status, tl))
        if not tl:
            return None, None, None

        # ptt: Potential Transition To List
        pttl = [p.iterkeys().next() for p in tl]
        logging.debug(pttl)

        for potential_transition_to in pttl:
            # test to see if it's a viable transition:
            logging.debug("test to see if transition is possible : {} -> {}".format(self.new.status, potential_transition_to))
            # try to find a possible transition... if no possible transition (transition was not defined on the model
            # it will always validate
            possible_fsm_transition = self._get_fsm_defined_transitions(self.new.status, potential_transition_to)
            if not possible_fsm_transition:
                logging.debug("transition: {} -> {} is possible since there was no transition defined on the model".format(
                    self.new.status, potential_transition_to
                ))
            if self.auto_transition_validation(possible_fsm_transition)[0]:
                # auto_update_functions:
                auf = next(obj[potential_transition_to] for obj in tl if potential_transition_to in obj)
                logging.debug("transition is possible  {} -> {}".format(self.new.status, potential_transition_to))
                return True, potential_transition_to, auf
            logging.debug("transition is not possible : {} -> {}".format(self.new.status, potential_transition_to))
        return None, None, None

    def _make_auto_transition(self):
        valid_available_transition, new_status, auto_update_functions = self._first_available_auto_transition()
        if not valid_available_transition:
            return False
        else:
            logging.debug("valid potential transition happening {}->{}".format(self.new.status, new_status))
            originals = self.new.status, self.new_status
            self.new.status = new_status
            self.new_status = new_status

            logging.debug("making sure new state is valid: {}".format(self.new.status))
            state_valid = self.state_valid()
            logging.debug("new state  {} is valid: {}".format(self.new.status, state_valid[0]))
            if not state_valid[0]:
                # set stuff back
                self.new.status, self.new_status = originals
                return False

            # if all good run all the autoupdates on that status
            for function in auto_update_functions:
                logging.debug("auto updating functions for transition")
                function(self.new)
            return True

    def make_auto_transitions(self):
        logging.debug("*************** STARTING AUTO TRANSITIONS *****************")
        any_transition_made = False
        while self._make_auto_transition():
            any_transition_made = True

        logging.debug("*************** ENDING AUTO TRANSITIONS ***************** auto_transitioned: {}".format(any_transition_made))
        return any_transition_made

    @cached_property
    def basic_validation(self):
        '''
        basic set of validations to make sure new state is correct
        :return: True or False
        '''

        setattr(self.new, 'old_instance', self.old)
        self.permissions = self.get_permissions(self.new)
        errors = []
        for validation_function in self.BASIC_VALIDATIONS:
            a = error_string(validation_function)(self.new)
            errors += a[1]
        delattr(self.new, 'old_instance')
        self.permissions = None
        return not len(errors), errors

    def map_errors(self, errors):
        return [self.VALID_ERRORS.get(error, error) for error in errors]

    @cached_property
    def total_validation(self):
        if not self.basic_validation[0]:
            return False, self.map_errors(self.basic_validation[1])

        if not self.skip_transition and not self.stateless:
            transitional = self.transitional_validation()
            if not transitional[0]:
                return False, self.map_errors(transitional[1])

        if not self.stateless:
            state_valid = self.state_valid()
            if not state_valid[0]:
                return False, self.map_errors(state_valid[1])

            if self.make_auto_transitions():
                self.new.save()
        return True, []

    @property
    def is_valid(self):
        return self.total_validation[0]

    @property
    def errors(self):
        return self.total_validation[1]
