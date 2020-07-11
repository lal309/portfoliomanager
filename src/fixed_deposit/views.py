from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView
)
from django.http import HttpResponseRedirect
from django.template import Context
from decimal import Decimal
from .models import FixedDeposit
from .fixed_deposit_helper import add_fd_entry, get_maturity_value
from shared.handle_get import *

# Create your views here.

class FixedDepositListView(ListView):
    template_name = 'fixed-deposits/fixed_deposit_list.html'
    queryset = FixedDeposit.objects.all() # <blog>/<modelname>_list.html
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        print(data)
        data['goal_name_mapping'] = get_all_goals_id_to_name_mapping()
        data['user_name_mapping'] = get_all_users()
        return data

class FixedDepositDetailView(DetailView):
    template_name = 'fixed-deposits/fixed_deposit_detail.html'
    #queryset = Ppf.objects.all()

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(FixedDeposit, id=id_)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        print(data)
        data['goal_str'] = get_goal_name_from_id(data['object'].goal)
        data['user_str'] = get_user_name_from_id(data['object'].user)
        return data

class FixedDepositDeleteView(DeleteView):
    template_name = 'fixed-deposits/fixed_deposit_delete.html'
    
    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(FixedDeposit, id=id_)

    def get_success_url(self):
        return reverse('fixed-deposits:fixed-deposit-list')

def add_fixed_deposit(request):
    # https://www.youtube.com/watch?v=Zx09vcYq1oc&list=PLLxk3TkuAYnpm24Ma1XenNeq1oxxRcYFT
    template = 'fixed-deposits/add_fixed_deposit.html'
    if request.method == 'POST':
        print(request.POST)
        if "submit" in request.POST:
            print("submit button pressed")
            number = request.POST['number']
            bank_name = request.POST['bank_name']
            start_date = request.POST['start_date']
            user = request.POST['user']
            time_period_days = Decimal(request.POST['time_period_days'])
            roi = Decimal(request.POST['roi'])
            principal = Decimal(request.POST['principal'])
            final_val = Decimal(request.POST['final_val'])
            goal = request.POST['goal']
            if goal != '':
                goal_id = Decimal(goal)
            else:
                goal_id = None
            notes = request.POST['notes']
            mat_date = request.POST['mat_date']
            add_fd_entry(number, bank_name, start_date, principal, time_period_days,
                    final_val, user, notes, goal_id, roi, mat_date)
        else:
            print("calculate button pressed")
            number = request.POST['number']
            bank_name = request.POST['bank_name']
            start_date = request.POST['start_date']
            user = request.POST['user']
            time_period_days = Decimal(request.POST['time_period_days'])
            principal = Decimal(request.POST['principal'])
            roi = Decimal(request.POST['roi'])
            notes = request.POST['notes']
            goal = request.POST['goal']
            mat_date, val = get_maturity_value(int(principal), start_date, float(roi), int(time_period_days))
            print("calculated value", val)
            users = get_all_users()
            context = {'users':users,'user':user, 'number':number, 'start_date':start_date, 'bank_name': bank_name, 'roi': roi,
                'time_period_days': time_period_days, 'principal': principal, 'final_val':val, 'notes': notes,
                'goal':goal, 'mat_date':mat_date, 'operation': 'Add Fixed Deposit'}
            return render(request, template, context=context)
    users = get_all_users()
    context = {'users':users, 'operation': 'Add Fixed Deposit'}
    return render(request, template, context)


def update_fixed_deposit(request, id):
    # https://www.youtube.com/watch?v=Zx09vcYq1oc&list=PLLxk3TkuAYnpm24Ma1XenNeq1oxxRcYFT
    template = 'fixed-deposits/add_fixed_deposit.html'
    if request.method == 'POST':
        print(request.POST)
        if "submit" in request.POST:
            print("submit button pressed")
            try:
                fd_obj = FixedDeposit.objects.get(id=id)
                fd_obj.number = request.POST['number']
                fd_obj.bank_name = request.POST['bank_name']
                fd_obj.start_date = request.POST['start_date']
                fd_obj.user = request.POST['user']
                fd_obj.time_period_days = Decimal(request.POST['time_period_days'])
                fd_obj.roi = Decimal(request.POST['roi'])
                fd_obj.principal = Decimal(request.POST['principal'])
                fd_obj.final_val = Decimal(request.POST['final_val'])
                goal = request.POST['goal']
                if goal != '':
                    fd_obj.goal = Decimal(goal)
                else:
                    fd_obj.goal = None
                fd_obj.notes = request.POST['notes']
                fd_obj.mat_date = request.POST['mat_date']
                fd_obj.save()
            except FixedDeposit.DoesNotExist:
                pass
        else:
            print("calculate button pressed")
            number = request.POST['number']
            bank_name = request.POST['bank_name']
            start_date = request.POST['start_date']
            user = request.POST['user']
            time_period_days = Decimal(request.POST['time_period_days'])
            principal = Decimal(request.POST['principal'])
            roi = Decimal(request.POST['roi'])
            notes = request.POST['notes']
            goal = request.POST['goal']
            mat_date, val = get_maturity_value(int(principal), start_date, float(roi), int(time_period_days))
            print("calculated value", val)
            users = get_all_users()()
            context = {'users':users,'user':user, 'number':number, 'start_date':start_date, 'bank_name': bank_name, 'roi': roi,
                'time_period_days': time_period_days, 'principal': principal, 'final_val':val, 'notes': notes,
                'goal':goal, 'mat_date':mat_date, 'operation': 'Edit Fixed Deposit'}
            return render(request, template, context=context)
        return HttpResponseRedirect("../")
    else:
        try:
            fd_obj = FixedDeposit.objects.get(id=id)
            # Always put date in %Y-%m-%d for chrome to show things properly
            users = get_all_users()
            context = {'users':users,'user':fd_obj.user, 'number':fd_obj.number, 'start_date':fd_obj.start_date.strftime("%Y-%m-%d"), 'bank_name':fd_obj.bank_name,
                    'roi':fd_obj.roi, 'time_period_days': fd_obj.time_period, 'principal': fd_obj.principal, 'final_val':fd_obj.final_val,
                    'notes':fd_obj.notes, 'goal':fd_obj.goal, 'mat_date':fd_obj.mat_date.strftime("%Y-%m-%d"),
                    'operation': 'Edit Fixed Deposit'}
        except FixedDeposit.DoesNotExist:
            context = {'operation': 'Edit Fixed Deposit'}
        return render(request, template, context=context)
