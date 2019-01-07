from django import template

register = template.Library()

@register.inclusion_tag('admin/users/country/submit_line_change_country.html', takes_context=True)
def submit_row_change_country(context):
    """
    Displays the row of buttons for delete and save.
    """
    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']
    is_global_schema = True if context['user'].profile.country.name == 'Global' else False
    ctx = {
        'opts': opts,
        'show_delete_link': (
            not is_popup and context['has_delete_permission'] and
            change and context.get('show_delete', True) and is_global_schema
        ),
        'show_save_as_new': not is_popup and change and save_as,
        'show_save_and_add_another': (
            context['has_add_permission'] and not is_popup and
            (not save_as or context['add'])
        ),
        'show_save_and_continue': not is_popup and context['has_change_permission'],
        'is_popup': is_popup,
        'show_save': True,
        'preserved_filters': context.get('preserved_filters'),
        'is_global_schema': is_global_schema,
    }
    if context.get('original') is not None:
        ctx['original'] = context['original']
    return ctx
