# -*- coding: utf-8 -*-
import datetime, re
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied #change error 
from .models import Penalty
from .forms import newPenaltyForm
from django.contrib.auth import get_user_model

@login_required
def redWine_home(request):
    return redWine_com(request, request.user.groups.all()[:1].get())

def redWine_com(request, committee):
    User = get_user_model()
    submitted=False
    showDeleted=False
    ownDelete=False
    editedUser=-1
    kom = request.user.groups.filter(name=committee)[:1].get();
    if request.method == 'POST':
        act=str(request.POST['act'])
        form = newPenaltyForm(data=request.POST)
        print(act)
        if act =='add':
            if int(form.data['amount'])<=10 and 1<len(form.data['reason'])<=100:
                #todo: sjekk at man gir til samme komite
                s=Penalty(
                    giver=     request.user,
                    committee= str(form.data['committee'].encode('utf8')),
                    to=        User.objects.get(pk=(int(form.data['to']))),
                    amount=    int(form.data['amount']),
                    reason=    str(form.data['reason'].encode('utf8'))
                    )
                s.save()
                editedUser=int(form.data['to'])
            else:
                raise PermissionDenied
                
        elif 'delete' in act: 
            #filter for kom
            penalty=Penalty.objects.get(pk=int(act.split(" ")[1]))
            if str(penalty.to.username) != str(request.user):
                penalty.deleted=True
                penalty.save()
                editedUser=penalty.to.id

        elif 'nuke' in act:
            #filter for kom
            for penalty in Penalty.objects.filter(to=User.objects.get(pk=int(act.split(" ")[1]))):
                if str(penalty.to.username) != str(request.user):
                    penalty.deleted=True
                    penalty.save()
                    editedUser=int(act.split(" ")[1])
                else:
                    ownDelete=True

        elif 'showhidden' in act:
            showDeleted=True
            editedUser=int(act.split(" ")[1])-1

        else:
            form=newPenaltyForm()

    #Penaltyer=Penalty.objects.all()
    committees = {}
    total = lambda user: sum([penalty.amount for penalty in user.penalties.filter(deleted=False, committee=kom)])
    for committee in request.user.groups.all():
        if 'redWine' in get_group_permissions(obj=committee):
            committees[committee] = [(user, total(user)) for user in committee.user_set.all()]

    return render(request, 'index.html', {  
        'committees'   : committees,
        'currCom'      : kom,
        'submittedNew' : submitted,
        'showDeleted'  : showDeleted,
        'editedUser'   : editedUser,
        'ownDelete'    : ownDelete,
        #'form' : form,
        })