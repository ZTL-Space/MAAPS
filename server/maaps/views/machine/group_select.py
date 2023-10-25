from django.http import HttpResponse
from django.template import loader
from maaps.views.functions.session import get_machines_from_group_session, find_session_redirect


def machine__group_select(request, group_name = ""):
    error = None
    all_machines = []
    if group_name != "" and group_name is not None:
        group_name = group_name
        try:
            request.session["group"] = group_name
           
        except Exception:
            error = "Group not found"
    all_machines = get_machines_from_group_session(request)
   

    template = loader.get_template('machine/group_select.html')
    return HttpResponse(template.render({
        'error': error,
        'url': './G:' + group_name,
        "group": group_name.replace('_',' '),
        'machines': all_machines,
       
    }, request))
