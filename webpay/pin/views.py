from django import http
from django.core.urlresolvers import reverse
from django.shortcuts import render

import commonware.log

from lib.solitude.api import client
from webpay.auth.decorators import user_verified
from webpay.auth.utils import get_user, set_user_has_pin
from webpay.pay import get_payment_url
from . import forms

log = commonware.log.getLogger('w.pin')


@user_verified
def create(request):
    form = forms.CreatePinForm()
    if request.method == 'POST':
        form = forms.CreatePinForm(uuid=get_user(request), data=request.POST)
        if form.is_valid():
            if hasattr(form, 'buyer'):
                res = client.change_pin(form.buyer, form.cleaned_data['pin'])
            else:
                res = client.create_buyer(form.uuid, form.cleaned_data['pin'])
            if form.handle_client_errors(res):
                set_user_has_pin(request, True)
                return http.HttpResponseRedirect(reverse('pin.confirm'))
    return render(request, 'pin/create.html', {'form': form})


@user_verified
def confirm(request):
    form = forms.ConfirmPinForm()
    if request.method == 'POST':
        form = forms.ConfirmPinForm(uuid=get_user(request), data=request.POST)
        if form.is_valid():
            return http.HttpResponseRedirect(get_payment_url())
    return render(request, 'pin/confirm.html', {'form': form})


@user_verified
def verify(request):
    form = forms.VerifyPinForm()
    if request.method == 'POST':
        form = forms.VerifyPinForm(uuid=get_user(request), data=request.POST)
        if form.is_valid():
            return http.HttpResponseRedirect(get_payment_url())
    return render(request, 'pin/verify.html', {'form': form})


@user_verified
def change(request):
    form = forms.ChangePinForm()
    if request.method == 'POST':
        form = forms.ChangePinForm(uuid=get_user(request), data=request.POST)
        if form.is_valid():
            res = client.change_pin(form.buyer, form.cleaned_data['pin'])
            if form.handle_client_errors(res):
                # TODO(Wraithan): Replace with proper redirect
                return render(request, 'pin/change_success.html',
                              {'form': form})
    return render(request, 'pin/change.html', {'form': form})