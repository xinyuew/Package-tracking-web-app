from datetime import datetime, timedelta
from mimetypes import guess_type

import easypost
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from forms import *
from track_utility import *

easypost.api_key = easypost_key


def welcome(request):
    if request.user.is_authenticated():
        return profile(request)

    return render(request, 'tracksite/welcome.html', {})


def add_track(request):
    track_num = request.POST.get('track_num', '')
    carrier = identify(track_num)

    if carrier == '':
        return redirect(reverse('profile'))

    try:
        profile = Profile.objects.get(user=request.user)
        track = profile.tracks.get(trackNum=track_num)
    except ObjectDoesNotExist:
        user = request.user

        # Get all tracks information of this user
        tracks = Profile.objects.get(user=user).tracks

        # Create a new track object
        try:
            tracker = easypost.Tracker.create(tracking_code=track_num, carrier=carrier)
        except:
            return render(request, 'tracksite/error.html', {})

        detail_dict = tracker.to_dict()
        details = json.dumps(detail_dict['tracking_details'])
        carrier = json.dumps(detail_dict['carrier'])

        est_date = None
        if 'est_delivery_date' in detail_dict:
            est_date = json.dumps(detail_dict['est_delivery_date'])

        details_json = json.loads(details)
        event = details_json[len(details_json) - 1]

        # for event in details:
        datetimes = format_date(event.get('datetime', ' '))
        event['datetime'] = datetimes

        # Check if details_json is not valid
        if details is None or details == "":
            return redirect(reverse('profile'))

        if est_date is not None and est_date != 'null':
            est_date = format_date(est_date)
            new_track = TrackInfo(details=details, trackNum=track_num, carrier=carrier, last_update=datetimes,
                                  est_delivery_date=est_date)
        else:
            new_track = TrackInfo(details=details, trackNum=track_num, carrier=carrier, last_update=datetimes)
        new_track.save()

        # Add this track object to this user's time line list
        tracks.add(new_track)

    return redirect(reverse('profile'))


def query(request):
    track_num = request.POST.get('track_num', '')

    carrier = identify(track_num)
    if carrier == '':
        return render(request, 'tracksite/error.html.html', {})

    try:
        tracker = easypost.Tracker.create(tracking_code=track_num, carrier=carrier)
    except:
        return render(request, 'tracksite/error.html', {})

    details = tracker.get('tracking_details')
    carrier = tracker.get('carrier')
    if details is None or details == [] or carrier is None:
        return redirect(reverse('error'))

    # format string in details
    for event in details:
        datetime = event.get('datetime', ' ')
        datetime = format_date(datetime)
        event['datetime'] = datetime
        event = format_message(event, carrier)

        city = event['tracking_location'].get('city', 'null')
        if city != 'null':
            event['tracking_location']['city'] = str(city).title()

    context = {'infos': details, 'carrier': carrier, 'tnum': track_num}
    if request.user.is_authenticated():
        context['profile'] = get_object_or_404(Profile, user=request.user)

    return render(request, 'tracksite/result.html', context)


def register(request):
    context = {}
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'tracksite/register.html', context)

    form = RegistrationForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'tracksite/register.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'],
                                        email=form.cleaned_data['email'],
                                        password=form.cleaned_data['password1'])
    new_user.save()

    profile = Profile(user=new_user,
                      first_name=form.cleaned_data['first_name'],
                      last_name=form.cleaned_data['last_name'],
                      email=form.cleaned_data['email'], )
    profile.save()

    # To authenticate a given username and password
    # it returns a User object if the password is valid for the given username.
    # If the password is invalid, authenticate() returns None.
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'])
    login(request, new_user)
    return redirect(reverse('profile'))


@login_required
def profile(request):
    context = {'user': request.user}
    profile = get_object_or_404(Profile, user=request.user)
    context['profile'] = profile
    tracks = Profile.objects.get(user=request.user).tracks.order_by('last_update').reverse()
    track_details = []

    for track in tracks.all():
        event = add_to_profile(track, request.user, track.id)
        track_details.append(event)

    for roommate in profile.roommates.all():
        profile_roommate = get_object_or_404(Profile, user=roommate)
        for track_roommate in profile_roommate.tracks.all():
            event_roommate = add_to_profile(track_roommate, roommate, track_roommate.id)
            track_details.append(event_roommate)

    track_details = sorted(track_details, key=lambda t: t['datetime'], reverse=True)
    context['track_details'] = track_details

    return render(request, 'tracksite/profile.html', context)


@login_required
def edit_profile(request):
    context = {}
    profile_to_edit = get_object_or_404(Profile, user=request.user)
    if request.method == 'GET':
        context['form'] = ProfileForm(instance=profile_to_edit)
        return render(request, 'tracksite/edit_profile.html', context)

    form = ProfileForm(request.POST, request.FILES, instance=profile_to_edit)

    if not form.is_valid():
        context['form'] = form
        return render(request, 'tracksite/edit_profile.html', context)

    user = profile_to_edit.user
    user.email = form.cleaned_data['email']
    user.first_name = form.cleaned_data['first_name']
    user.last_name = form.cleaned_data['last_name']

    user.save()
    form.save()

    return redirect(reverse('profile'))


@login_required
def get_photo(request, user_id):
    user = User.objects.get(id=user_id)
    profile = get_object_or_404(Profile, user=user)

    if not profile.picture:
        raise Http404

    content_type = guess_type(profile.picture.name)
    return HttpResponse(profile.picture, content_type=content_type)


@login_required
def add_roommate(request):
    context = {}
    profile = get_object_or_404(Profile, user=request.user)
    roommates = profile.roommates.all()
    context['roommates'] = roommates
    context['profile'] = profile
    if request.method == 'GET':
        context['form'] = RoommateForm()
        return render(request, 'tracksite/roommates.html', context)

    form = RoommateForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        return render(request, 'tracksite/roommates.html', context)

    if form.cleaned_data['username'] == request.user.username:
        context['errors'] = "Cannot add yourself"
        return render(request, 'tracksite/roommates.html', context)

    new_roommate = User.objects.get(username=form.cleaned_data['username'])
    if new_roommate in profile.roommates.all():
        context['errors'] = "This user is in your roommate list!"
        return render(request, 'tracksite/roommates.html', context)

    return redirect(reverse('send_email', kwargs={'user_id': new_roommate.id}))


@login_required
def remove_roommate(request, user_id):
    user = User.objects.get(id=user_id)
    profile = get_object_or_404(Profile, user=request.user)

    if user in profile.roommates.all():
        profile.roommates.remove(user)

    return redirect(reverse('profile'))


@login_required
def send_email(request, user_id):
    context = {}
    user = User.objects.get(id=user_id)
    profile = Profile.objects.get(user=user)
    email = profile.email
    context['email'] = email

    token = default_token_generator.make_token(user)
    email_body = """
        Please click on the link to confirm that you will be added as %s's roommate://%s%s
        """ % (request.user.first_name, request.get_host(),
               reverse('verify_add_roommate', args=(user.username, token, request.user.username)))

    send_mail(subject="Verification from youTrack",
              message=email_body,
              from_email="system@youtrack.com",
              recipient_list=[email])
    context['success_send_email_messages'] = "Request has been send to your roommate! Wait for verification."
    context['form'] = RoommateForm()

    return render(request, 'tracksite/roommates.html', context)


def verify_add_roommate(request, username, token, request_username):
    context = {}
    user = get_object_or_404(User, username=username)
    request_user = get_object_or_404(User, username=request_username)
    context['request_user_first'] = request_user.first_name
    context['request_user_last'] = request_user.last_name
    context['request_user'] = request_user
    context['target_user'] = user

    if request_user.is_authenticated():
        for s in Session.objects.all():
            if int(s.get_decoded().get('_auth_user_id')) == request_user.id:
                s.delete()

    if not default_token_generator.check_token(user, token):
        raise Http404

    return render(request, "tracksite/verify_roommate.html", context)


def add_as_roommate(request):
    if 'request_username' not in request.POST or not request.POST['request_username']:
        raise Http404
    if 'target_username' not in request.POST or not request.POST['target_username']:
        raise Http404

    request_username = request.POST['request_username']
    target_username = request.POST['target_username']
    request_user = User.objects.get(username=request_username)
    target_user = User.objects.get(username=target_username)
    profile = get_object_or_404(Profile, user=request_user)

    if target_user not in profile.roommates.all():
        profile.roommates.add(target_user)

    return render(request, "tracksite/login.html", {})


def find_upcoming_delivery(request):
    if not request.user.is_authenticated():
        return JsonResponse({})

    now = datetime.now()
    threshold = now + timedelta(hours=12)
    result = {}
    try:
        user = User.objects.get(username=request.user.username)
        tracks = Profile.objects.get(user=user).tracks.filter(est_delivery_date__isnull=False)

        # check user's package
        for package in tracks:
            est_time = package.est_delivery_date.replace(tzinfo=None)
            if threshold > est_time > now:
                result[package.trackNum] = str(est_time)

        # check user's roommates' package
        for roommate in Profile.objects.get(user=user).roommates.all():
            tracks = Profile.objects.get(user=roommate).tracks.filter(est_delivery_date__isnull=False)
            for package in tracks:
                est_time = package.est_delivery_date.replace(tzinfo=None)
                if threshold > est_time > now:
                    result[package.trackNum] = str(est_time)

    except ObjectDoesNotExist:
        return JsonResponse({})

    return JsonResponse(result)


def query_with_num(request, num):
    track_num = num
    carrier = identify(track_num)
    if carrier == '':
        return render(request, 'tracksite/error.html', {})

    try:
        tracker = easypost.Tracker.create(tracking_code=track_num, carrier=carrier)
    except:
        return render(request, 'tracksite/error.html', {})

    details = tracker.get('tracking_details')
    carrier = tracker.get('carrier')
    if details is None or details == [] or carrier is None:
        return redirect(reverse('error'))

    # format string in details
    for event in details:
        event['datetime'] = format_date(event.get('datetime', ' '))
        event = format_message(event, carrier)

        city = event['tracking_location'].get('city', 'null')
        if city != 'null':
            event['tracking_location']['city'] = str(city).title()

    context = {'infos': details, 'carrier': carrier, 'tnum': track_num}
    if request.user.is_authenticated():
        context['profile'] = get_object_or_404(Profile, user=request.user)

    return render(request, 'tracksite/result.html', context)


def error_page(request):
    return render(request, 'tracksite/error.html', {})


def delete_track(request, track_id):
    track = TrackInfo.objects.get(id=track_id)
    profile = get_object_or_404(Profile, user=request.user)

    if track in profile.tracks.all():
        track.delete()

    return redirect(reverse('profile'))
