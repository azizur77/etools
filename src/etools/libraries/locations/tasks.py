import celery

from carto.exceptions import CartoException
from carto.sql import SQLClient
from celery.utils.log import get_task_logger

from django.utils.encoding import force_text
from django.db import transaction

from unicef_locations.models import CartoDBTable, Location
from unicef_locations.auth import LocationsCartoNoAuthClient

from etools.libraries.locations.task_utils import (
    get_location_ids_in_use,
    get_cartodb_locations,
    save_location_remap_history,
    validate_remap_table,
    duplicate_pcodes_exist,
    create_location,
)

logger = get_task_logger(__name__)


@celery.current_app.task()
def validate_locations_in_use(carto_table_pk):
    try:
        carto_table = CartoDBTable.objects.get(pk=carto_table_pk)
    except CartoDBTable.DoesNotExist as e:
        logger.exception('Cannot retrieve CartoDBTable with pk: %s', carto_table_pk)
        raise e

    database_pcodes = []
    for row in Location.objects.all_locations().filter(gateway=carto_table.location_type).values('p_code'):
        database_pcodes.append(row['p_code'])

    auth_client = LocationsCartoNoAuthClient(base_url="https://{}.carto.com/".format(carto_table.domain))
    sql_client = SQLClient(auth_client)

    try:
        qry = sql_client.send('select array_agg({}) AS aggregated_pcodes from {}'.format(
            carto_table.pcode_col,
            carto_table.table_name,
        ))
        new_carto_pcodes = qry['rows'][0]['aggregated_pcodes']

        remapped_pcode_pairs = []
        if carto_table.remap_table_name:
            remap_qry = 'select old_pcode::text, new_pcode::text from {}'.format(carto_table.remap_table_name)
            remapped_pcode_pairs = sql_client.send(remap_qry)['rows']

    except CartoException as e:
        logger.exception("CartoDB exception occured during the data validation.")
        raise e

    remap_old_pcodes = [remap_row['old_pcode'] for remap_row in remapped_pcode_pairs]
    orphaned_pcodes = set(database_pcodes) - (set(new_carto_pcodes) | set(remap_old_pcodes))
    orphaned_location_ids = Location.objects.all_locations().filter(p_code__in=list(orphaned_pcodes))

    # if location ids with no remap in use are found, do not continue the import
    location_ids_bnriu = get_location_ids_in_use(orphaned_location_ids)
    if location_ids_bnriu:
        msg = "Location ids in use without remap found: {}". format(','.join([str(iu) for iu in location_ids_bnriu]))
        logger.exception(msg)
        raise Exception(msg)

    return True


@celery.current_app.task # noqa: ignore=C901
def update_sites_from_cartodb(carto_table_pk):
    results = []

    try:
        carto_table = CartoDBTable.objects.get(pk=carto_table_pk)
    except CartoDBTable.DoesNotExist:
        logger.exception('Cannot retrieve CartoDBTable with pk: %s', carto_table_pk)
        return results

    auth_client = LocationsCartoNoAuthClient(base_url="https://{}.carto.com/".format(carto_table.domain))
    sql_client = SQLClient(auth_client)
    sites_created = sites_updated = sites_remapped = sites_not_added = 0

    try:
        # query cartodb for the locations with geometries
        carto_succesfully_queried, rows = get_cartodb_locations(sql_client, carto_table)

        if not carto_succesfully_queried:
            return results
    except CartoException:  # pragma: no-cover
        logger.exception("CartoDB exception occured")
    else:
        # validations
        # get the list of the existing Pcodes and previous Pcodes from the database
        database_pcodes = []
        for row in Location.objects.all_locations().filter(gateway=carto_table.location_type).values('p_code'):
            database_pcodes.append(row['p_code'])

        # get the list of the new Pcodes from the Carto data
        new_carto_pcodes = [str(row[carto_table.pcode_col]) for row in rows]

        # validate remap table contents
        remap_table_valid, remapped_pcode_pairs, remap_old_pcodes, remap_new_pcodes = \
            validate_remap_table(database_pcodes, new_carto_pcodes, carto_table, sql_client)

        if not remap_table_valid:
            return results

        # check for  duplicate pcodes in both local and Carto data
        if duplicate_pcodes_exist(database_pcodes, new_carto_pcodes, remap_old_pcodes):
            return results

        # wrap Location tree updates in a transaction, to prevent an invalid tree state due to errors
        with transaction.atomic():
            # disable tree 'generation' during single row updates, rebuild the tree after.
            # this should prevent errors happening (probably)due to invalid intermediary tree state
            with Location.objects.disable_mptt_updates():
                for row in rows:
                    carto_pcode = str(row[carto_table.pcode_col]).strip()
                    site_name = row[carto_table.name_col]

                    if not site_name or site_name.isspace():
                        logger.warning("No name for location with PCode: {}".format(carto_pcode))
                        sites_not_added += 1
                        continue

                    parent = None
                    parent_code = None
                    parent_instance = None

                    # attempt to reference the parent of this location
                    if carto_table.parent_code_col and carto_table.parent:
                        msg = None
                        parent = carto_table.parent.__class__
                        parent_code = row[carto_table.parent_code_col]
                        try:
                            parent_instance = Location.objects.get(p_code=parent_code)
                        except Location.MultipleObjectsReturned:
                            msg = "Multiple locations found for parent code: {}".format(
                                parent_code
                            )
                        except Location.DoesNotExist:
                            msg = "No locations found for parent code: {}".format(
                                parent_code
                            )
                        except Exception as exp:
                            msg = force_text(exp)

                        if msg is not None:
                            logger.warning(msg)
                            sites_not_added += 1
                            continue

                    # check if the Carto location should be remapped to an old location
                    remapped_old_pcodes = set()
                    if carto_table.remap_table_name and len(remapped_pcode_pairs) > 0:  # pragma: no-cover
                        for remap_row in remapped_pcode_pairs:
                            if carto_pcode == remap_row['new_pcode']:
                                remapped_old_pcodes.add(remap_row['old_pcode'])

                    # create the location or update the existing based on type and code
                    succ, sites_not_added, sites_created, sites_updated, sites_remapped, \
                        partial_results = create_location(
                            carto_pcode, carto_table,
                            parent, parent_instance, remapped_old_pcodes,
                            site_name, row,
                            sites_not_added, sites_created,
                            sites_updated, sites_remapped
                        )

                    results += partial_results

                # crete remap history, and remap relevant etools enitites(interventions, travels, etc..)
                # from the remapped location, which is to be archived, to the new location
                if results:
                    save_location_remap_history(results)

                orphaned_old_pcodes = set(database_pcodes) - (set(new_carto_pcodes) | set(remap_old_pcodes))
                if orphaned_old_pcodes:  # pragma: no-cover
                    logger.warning("Archiving unused pcodes: {}".format(','.join(orphaned_old_pcodes)))
                    Location.objects.filter(p_code__in=list(orphaned_old_pcodes)).update(is_active=False)

            # rebuild location tree
            Location.objects.rebuild()

    logger.warning("Table name {}: {} sites created, {} sites updated, {} sites remapped, {} sites skipped".format(
        carto_table.table_name, sites_created, sites_updated, sites_remapped, sites_not_added))

    # return results


@celery.current_app.task(bind=True)
def cleanup_obsolete_locations(self, carto_table_pk):

    try:
        carto_table = CartoDBTable.objects.get(pk=carto_table_pk)
    except CartoDBTable.DoesNotExist as e:
        logger.exception('Cannot retrieve CartoDBTable with pk: %s', carto_table_pk)
        raise e

    database_pcodes = []
    for row in Location.objects.all_locations().filter(gateway=carto_table.location_type).values('p_code'):
        database_pcodes.append(row['p_code'])

    auth_client = LocationsCartoNoAuthClient(base_url="https://{}.carto.com/".format(carto_table.domain))
    sql_client = SQLClient(auth_client)

    try:
        qry = sql_client.send('select array_agg({}) AS aggregated_pcodes from {}'.format(
            carto_table.pcode_col,
            carto_table.table_name,
        ))
        new_carto_pcodes = qry['rows'][0]['aggregated_pcodes']

        remapped_pcode_pairs = []
        if carto_table.remap_table_name:
            remap_qry = 'select old_pcode::text, new_pcode::text from {}'.format(carto_table.remap_table_name)
            remapped_pcode_pairs = sql_client.send(remap_qry)['rows']

    except CartoException as e:
        logger.exception("CartoDB exception occured during the data validation.")
        raise e

    remapped_pcodes = [remap_row['old_pcode'] for remap_row in remapped_pcode_pairs]
    remapped_pcodes += [remap_row['new_pcode'] for remap_row in remapped_pcode_pairs]
    deleteable_pcodes = set(database_pcodes) - (set(new_carto_pcodes) | set(remapped_pcodes))

    for deleteable_pcode in deleteable_pcodes:
        try:
            deleteable_location = Location.objects.all_locations().get(p_code=deleteable_pcode)
        except Location.DoesNotExist:
            logger.warning("Cannot find orphaned pcode {}.".format(deleteable_pcode))
        else:
            if deleteable_location.is_leaf_node():
                logger.info("Deleting orphaned and unused location with pcode {}".format(deleteable_location.p_code))
                deleteable_location.delete()


@celery.current_app.task
def catch_task_errors():
    pass


class BnriuException(Exception):
    pass
