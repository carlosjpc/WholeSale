from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required

@login_required
def login_redirect(request):
    user = request.user
    x = user.groups.filter(name='Designer').count()
    if x == 1:
        return HttpResponseRedirect("/designer/ctrl_panel/")
    else:
        return HttpResponseRedirect("/showroom/ctrl_panel/")
