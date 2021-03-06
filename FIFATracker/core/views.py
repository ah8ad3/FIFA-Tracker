from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

import logging
import os
import shutil
import shlex
import subprocess

from collections import Counter

from core.session_utils import del_session_key, set_currency, get_current_user, get_fifa_edition, get_career_user
from .fifa_utils import get_team_name
from players.models import DataUsersTeams
from .models import CareerSaveFileModel
from .forms import CareerSaveFileForm


def upload_career_save_file(request):
    if not request.user.is_authenticated:
        messages.error(request, _(
            'Only authenticated users are allowed to upload files.'))
        return redirect('home')

    # Check if user already uploaded a file and it's not processed yet
    cs_model = CareerSaveFileModel.objects.filter(
        user_id=request.user.id).first()
    user = User.objects.get(username=request.user)

    if cs_model:
        if cs_model.file_process_status_code == 0:
            # File is being processed
            pass
        elif cs_model.file_process_status_code == 1:
            # Error
            cs_model.delete()
        elif cs_model.file_process_status_code == 2:
            # Done
            user.profile.is_save_processed = True
            user.save()
            cs_model.delete()

        return render(request, 'upload.html', {'cs_model': cs_model, 'upload_completed': True})

    if request.method == 'POST':
        form = CareerSaveFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Clear previous save data from session
            del_session_key(request, "career_user")

            fifa_edition = int(request.POST.get('fifa_edition'))

            # Supported FIFA Editions.
            valid_fifa_editions = (17, 18, 19)
            if fifa_edition not in valid_fifa_editions:
                data = {'is_valid': False}
                return JsonResponse(data)

            form = form.save(commit=False)
            form.user = request.user
            form.save()

            user.profile.is_save_processed = False
            user.profile.fifa_edition = fifa_edition
            user.save()

            # Run "process_career_file.py"
            if settings.DEBUG:
                python_ver = "python"   # My LocalHost
            else:
                python_ver = "python3.6"

            # python manage.py runscript process_career_file --script-args 14 18
            command = "{} manage.py runscript process_career_file --script-args {} {}".format(
                python_ver, request.user.id, fifa_edition)
            args = shlex.split(command)
            subprocess.Popen(args, close_fds=True)

            data = {'is_valid': True}
        else:
            data = {'is_valid': False}

        return JsonResponse(data)
    else:
        form = CareerSaveFileForm()

    return render(request, 'upload.html', {'form': form, 'cs_model': None})


def process_status(request):
    if not request.user.is_authenticated:
        data = {"status": "user not authenticated"}
        return JsonResponse(data)

    cs_model = CareerSaveFileModel.objects.filter(
        user_id=request.user.id).first()
    if cs_model:
        status_code = cs_model.file_process_status_code
        status_msg = cs_model.file_process_status_msg

        if not status_msg:
            status_msg = _("Processing Career Save File.")

        if cs_model.file_process_status_code == 0:
            # File is being processed
            pass
        elif cs_model.file_process_status_code == 1:
            # Error
            cs_model.delete()
        elif cs_model.file_process_status_code == 2:
            # Done
            user = User.objects.get(username=request.user)
            user.profile.is_save_processed = True
            user.save()
            cs_model.delete()

        data = {
            "status_code": status_code,
            "status_msg": status_msg,
        }
    else:
        data = {
            "status_code": 0,
            "status_msg": _("Done?? Try to refresh website."),
        }

    return JsonResponse(data)


def abort_upload(request):
    user = request.user
    if not user.is_authenticated:
        messages.error(request, _('Not authenticated.'))
        return redirect('home')

    logging.info("{} pressed abort button".format(user))

    cs_model = CareerSaveFileModel.objects.filter(user_id=user.id)
    if cs_model:
        # Delete original uploaded file
        for model in cs_model:
            fpath = os.path.join(settings.MEDIA_ROOT, str(model.uploadedfile))
            if os.path.isfile(fpath):
                try:
                    os.remove(fpath)
                    # Delete Model
                    model.delete()
                except PermissionError:
                    messages.error(request, _('File is still processed.'))

    # Delete Files
    careersave_data_path = os.path.join(settings.MEDIA_ROOT, user.username, "data")
    if os.path.exists(careersave_data_path):
        try:
            shutil.rmtree(careersave_data_path)
        except PermissionError:
            messages.error(request, _('File is still processed.'))

    return redirect('home')


def privacypolicy(request):
    return render(request, 'privacy.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def donate(request):
    return render(request, 'donate.html')


def home(request):
    data = User.objects.prefetch_related('careerusers').values(
        'careerusers__clubteamid', 'careerusers__nationalteamid'
    )

    fifa_edition = get_fifa_edition(request)

    clubs = list()
    nationalteams = list()
    all_teams = list()

    for u in data:
        club = u['careerusers__clubteamid']
        if club is not None and int(club) > 0:
            clubs.append(club)
            all_teams.append(club)

        nationalteam = u['careerusers__nationalteamid']
        if (nationalteam is not None) and int(nationalteam) > 0:
            nationalteams.append(nationalteam)
            all_teams.append(nationalteam)

    db_teams = list(DataUsersTeams.objects.for_user(
        "guest").all().filter(Q(teamid__in=all_teams)).values())

    count_all_teams = Counter(all_teams).most_common()

    max_teams_display = 30  # Max number of most popular teams to be displayed on homepage
    users_clubs = list()
    users_nationalteams = list()
    teamname = ""
    for team in count_all_teams:
        teamname = get_team_name(db_teams, team[0])
        if team[0] in clubs and len(users_clubs) < max_teams_display:
            users_clubs.append(
                {'id': team[0], 'managers': team[1], 'teamname': teamname, })
        elif team[0] in nationalteams and len(users_nationalteams) < max_teams_display:
            users_nationalteams.append(
                {'id': team[0], 'managers': team[1], 'teamname': teamname, })

    context = {
        'users_clubs': users_clubs,
        'users_nationalteams': users_nationalteams,
        'fifa_edition': fifa_edition,
    }
    return render(request, 'home.html', context=context)
