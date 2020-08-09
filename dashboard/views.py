#
# Copyright (c) 2020. Betterworks, Inc. All Rights Reserved.
#
# Author: adithya.bhat@gmail.com (Adithya bhat)
#
# Module which has two endpoints to get analytical data regarding
# scrum management of an organisation
#
# First endpoint:
# Method: GET
# URL: http://<IP>/dashboard/depatments?on_track_filter=2 weeks&recently_upd_filter=3 weeks
# Description: Rest endpont to get all the departments of an organisation and
# objectives on tack percentile and recently updated objectives percentile for the date filtered
# If no params are given default 
# `on_track_filter`= 1 weeks
# `recently_upd_filter`= 2 weeks
#
# Response(success):
# {"status": "OK", "data": {"objectives_on_track": {"date_since": "Friday 07/31", "on_track": 1, "total": 3,
# "on_track_ratio": 33}, "objectives_updated_recently": {"date_since": "2 weeks", "update_ratio": 67, "change": 0,
# "percentage_change": 0.0, "direction": "up"}, "departments": [{"name": "Product", "teams_count": 2, "users_count": 2,
# "objectives_count": 1, "objectives_on_track_ratio": 0}, {"name": "Engineering", "teams_count": 1, "users_count": 1,
# "objectives_count": 2, "objectives_on_track_ratio": 50}, {"name": "Marketing", "teams_count": 0, "users_count": 0,
# "objectives_count": 0, "objectives_on_track_ratio": "--"}]}}
#
# `objectives_on_track` has the info about on track objectives since the mentioned date
# `objectives_updated_recently` has the info about objectives recently updated since the mentioned date
# `departments` has all the info about departments
#
# Response(errror):
# {"status": "ERROR", data: <error message>}
#
# Second endpoint
# Method: GET
# URL: http://<IP>/dashboard/teams?department_name=Product
# Description: Rest endpont to get info about all the teams of a department
#
# Response(success):
# {"status": "OK", "data": {"teams": [{"team_leader": "Kailash", "members": []}]}}
# Response(error):
# {"status": "ERROR", "data": <error message>}
import logging 

from datetime import date, timedelta
from json import dumps
from traceback import format_exc

from django.db.models import Q
from django.shortcuts import HttpResponse, render

from .models import Department, Teams, Objectives

# Create your views here.
logger = logging.getLogger(__name__)

def get_departments(request):
    """
    Rest endpoint to get departments and analytics on recently updated objectives
    and on track objectives.
    Returns(HTTP response):
    django_template_variable
    {
        ## On track objectives analysis
        "objectives_on_track": {
            # Ananlysis since this date
            "date_since": "Friday 07/31", 
            "on_track": 1, 
            "total": 3,
            "on_track_ratio": 33
        }, 
        ## Recently updated objectives analysis
        "objectives_updated_recently": {
            "date_since": "2 weeks", 
            "update_ratio": 67, 
            # Change in objectives since last week
            "change": 0,
            "percentage_change": 0.0, 
            # "up" if change is positive else "down"
            "direction": "up"
        }, 
        "departments": [
            {"name": "Product", "teams_count": 2, "users_count": 2,
                "objectives_count": 1, "objectives_on_track_ratio": 0}, 
            {"name": "Engineering", "teams_count": 1, "users_count": 1,
                "objectives_count": 2, "objectives_on_track_ratio": 50}, 
            {"name": "Marketing", "teams_count": 0, "users_count": 0,
                "objectives_count": 0, "objectives_on_track_ratio": "--"}
        ]

    }
    """
    if request.method == "GET":
        resp = {}
        try:
            logger.info("Recieved a request get all the departments and "
                        "analysis on objectives.")
            # Get the on track date filter if provided
            objective_on_track_filter = request.GET.get(
                                      "on_track_filter", None)
            # Get on track objectives json
            on_track_objective_json = _get_objectives_on_tack_analysis(
                                    objective_on_track_filter)
            logger.debug("On track objectives analytical data: %s" 
                         % str(on_track_objective_json))
            resp["objectives_on_track"] = on_track_objective_json
            # Get recently updated date filter if provided
            objective_recently_upd_filter = request.GET.get(
                                        "recently_upd_filter", None)
            # Get recently updated objectives json
            updated_objective_json = _get_objectives_recently_updated_analysis(
                                objective_recently_upd_filter)
            logger.debug("Objectives updated recently analytical data: %s" 
                         % str(updated_objective_json))
            resp["objectives_updated_recently"] = updated_objective_json
            # Get all the departments and its info
            depts = _get_all_departments()
            logger.debug("All departments json: %s" % str(depts))
            resp["departments"] = depts
            logger.info("Departments and objectives analytical output "
                        "response: %s" % str(resp))
            return render(request, 'departments.html', resp)
        except Exception as err:
            logger.error("Error while getting departments and objectives "
                         "analyticl data, Error: %s, Stack: %s" 
                         % (str(err), format_exc()))
    return render(request, 'error.html')

def _get_objectives_on_tack_analysis(objective_on_track_filter):
    """
    Function to get objectives on track analysis
    Args:
        objective_on_track_filter - date since the analysis to be done
                                    default is 1 weeks
    Returns:
        {
            "date_since": "Friday 07/31", # Ananlysis since this date
            "on_track": 1, # on track objectives
            "total": 3, # total objectives
            "on_track_ratio": 33 # on track ratio
        }
    """
    on_track_obj_json = {}
    objective_on_track_filter_date = None
    if objective_on_track_filter is None:
        # If the filter is none, default is 1 week
        objective_on_track_filter_date = _get_filter_date(1)
        objective_on_track_filter = "1 week"
    else:
        num, unit = objective_on_track_filter.split(" ")
        objective_on_track_filter_date =  _get_filter_date(int(num), unit)
    logger.info("Objectives on track filter: %s" % objective_on_track_filter)
    on_track_obj_json["date_since"] = objective_on_track_filter_date.strftime(
                                    "%A %m/%d")
    on_track_objectives, total_objectives = _get_on_track_objectives(
                                          objective_on_track_filter_date)
    on_track_obj_json["on_track"] = on_track_objectives
    on_track_obj_json["total"] = total_objectives
    on_track_obj_json["on_track_ratio"] = round(
                                        on_track_objectives / 
                                        total_objectives * 100) \
                                        if total_objectives else "--"
    return on_track_obj_json

def _get_objectives_recently_updated_analysis(objective_recently_upd_filter):
    """
    Function to get updated objectives analysis
    Args:
        objective_recently_upd_filter - date since the analysis to be done
                                        default is 2 weeks
    Returns:
       {
            "date_since": "2 weeks", # date since analysis to be done
            "update_ratio": 67,  # updated objectives to total objectives ratio
            "change": 0, # change in objectives since last week
            "percentage_change": 0.0, # percentage change 
            "direction": "up" # "up" if change is positive else "down"
        }
    """
    recently_updated_obj_json = {}
    objective_recently_upd_filter_date = None
    if objective_recently_upd_filter is None:
        # If the filter is None, default is: 2 weeks
        objective_recently_upd_filter = "2 weeks"
        objective_recently_upd_filter_date = _get_filter_date(2)
        objective_recently_upd_filter_mid_date = _get_filter_date(1)
    else:
        num, unit = objective_recently_upd_filter.split(" ")
        num = int(num) / 2
        objective_recently_upd_filter_date =  _get_filter_date(num, unit) 
        objective_recently_upd_filter_mid_date = _get_filter_date(num/2, unit) 
    logger.info("Objectives recently updated filter: %s" 
                % objective_recently_upd_filter)
    recently_updated_obj_json["date_since"] = objective_recently_upd_filter
    updated_objectives, total_objectives = _get_updated_objectives(
                                         objective_recently_upd_filter_date)
    recently_updated_obj_json["update_ratio"] = round(
                                              updated_objectives / 
                                              total_objectives * 100) \
                                              if total_objectives else "--"
    # Get recently updated objectives between last week and last two weeks
    last_updated_objectives, \
    last_total_objectives = _get_updated_objectives_bw_dates(
                          objective_recently_upd_filter_date,
                          objective_recently_upd_filter_mid_date)
    # Get recently updated objectives between today and last week
    cur_updated_objectives, \
    cur_total_objectives = _get_updated_objectives(
                         objective_recently_upd_filter_mid_date)
    # Get change in no of objectives updated last week in comparison
    # with week before that
    change_in_objectives_json = _get_change_in_updates(
                              last_updated_objectives, last_total_objectives,
                              cur_updated_objectives, cur_total_objectives)
    recently_updated_obj_json.update(change_in_objectives_json)
    return recently_updated_obj_json           

def _get_change_in_updates(last_updated_objectives, last_total_objectives,
                           cur_updated_objectives, cur_total_objectives):
    """
    Function to get the change in objectives metrics
    Args:
        last_updated_objectives - objectives updated in the previous week
        last_total_objectives - total objectives in the previous week
        cur_updated_objectives - objectives updated in the current week
        cur_total_objectives - total objectives in the current week
    Returns:
        {
            change": 0, # Change in objectives
            "percentage_change": 0.0, # Change percentage
            "direction": "up" # direction of change
        }
    """
    change_in_objectives_json = {}
    change_in_updates = cur_updated_objectives - last_updated_objectives
    if change_in_updates < 0:
        direction = "down"
        change_in_updates = change_in_updates * (-1)
        change_percentage = round((last_updated_objectives / last_total_objectives -
                            cur_updated_objectives / cur_total_objectives) * 100) \
                            if cur_total_objectives and last_total_objectives \
                            else "--"
    else:
        direction = "up"
        change_percentage = round((cur_updated_objectives / cur_total_objectives - 
                            last_updated_objectives / last_total_objectives) * 100) \
                            if cur_total_objectives and last_total_objectives \
                            else "--" 
    change_in_objectives_json["change"] = change_in_updates
    change_in_objectives_json["percentage_change"] = change_percentage
    change_in_objectives_json["direction"] = direction
    logger.debug("Change in updated objectives: %s" 
                 % str(change_in_objectives_json))
    return change_in_objectives_json
    
def _get_filter_date(number, unit="weeks"):
    """
    Function to get the date before the given date inputs
    Args:
        number - no of units
        unit - 'weeks', 'months', 'years'; default 'weeks'
    Returns:
        current_date - days(number * unit)
    """
    unit = unit.lower()
    interval = 7
    if unit == "weeks":
        interval = number * 7
    elif unit == "months":
        interval = number * 30
    elif unit == "years":
        interval = number * 365
    return (date.today() - timedelta(days=interval))

def _get_all_departments():
    """
    Function to get all the departments info
    Returns:
        {
            "name": "Product", # Dept name
            "teams_count": 2, # total no of teams in the dept
            "users_count": 2, # Total no of employees in the dept
            "objectives_count": 1, # tot no of objectives
            "objectives_on_track_ratio": 0 # Objective on track ratio
        }
    """
    res = []
    departments = Department.objects.all()
    for dept in departments:
        # Get the team count, user count objectives count and on track ratio
        teams_count, users_count, \
        objectives_count, on_track_objectives = _get_dept_teams(dept)
        dept_details = {
            "name": dept.name,
            "teams_count": teams_count,
            "users_count": users_count,
            "objectives_count": objectives_count,
            "objectives_on_track_ratio": round(
                on_track_objectives /
                objectives_count * 100) if objectives_count else "--"
        }
        res.append(dept_details)
    return res

def _get_dept_teams(dept):
    """
    Get teams count, users count, objectives count, on_track_objectives for a dept
    Args:
        dept - department object
    Returns:
        teams_count - total no of teams
        users_count - total no of users
        objectives_count - total no of objectives 
        on_track_objectives - total no of on track objectives
    """
    teams_count = users_count = objectives_count = on_track_objectives = 0
    for team in  dept.teams_set.all():
        teams_count += 1
        users_count, objectives_count, \
        on_track_objectives = _get_team_users(team, users_count,
                                             objectives_count, on_track_objectives)
    return (teams_count, users_count, objectives_count, on_track_objectives)


def _get_team_users(team, users_count, objectives_count, on_track_objectives):
    """
    Function to get the no of users, objectives and on track objectives for a team
    Args:
        team - team object
        users_count - cumulative users count
        objectives_count - cumulative objectives count
        on_track_objectives - cumulative on track objectives count
    Returns:
        users_count - total no of users in a team
        objectives_count - total no of objectives for the team
        on_track_objectives - total no of on track objectives for the team
    """
    for user in team.users_set.all():
        users_count += 1
        objectives_count, on_track_objectives =  _get_user_objectives(
                                              user, 
                                              objectives_count, 
                                              on_track_objectives)
    return (users_count, objectives_count, on_track_objectives)

def _get_user_objectives(
        user, objectives_count=0, 
        on_track_objectives=0):
    """
    Function to get the total objectives and on track objectives for a user
    Args:
        user - user object
        objectives_count - cumulative objectives count
        on_track_objectives - cumulative on track objectives count
    Returns:
        objectives_count - total no of objectives for an user
        on_track_objectives - total no of on track objectives for an user
    """
    for objective in user.objectives_set.all():
        objectives_count += 1
        completed_keyresults_set = objective.keyresults_set
        if completed_keyresults_set.count():
            completed_keyresults = completed_keyresults_set.filter(
                                 ~Q(status="Complete"))
            if not completed_keyresults:
                # If none of the key results are pending
                on_track_objectives += 1
    return (objectives_count, on_track_objectives)

def _get_on_track_objectives(
        filter_date, objectives_count=0, 
        on_track_objectives=0):
    """
    Function to get the objectives count and on track objectives after filter_date
    Args:
        filter_date - date after which the objectives count and on_track_objectives
                       to be retreived
    Returns:
        objectives_count - total objectives count
        on_track_objectives - on track objectives count after filter_date
    """
    for objective in Objectives.objects.all():
        objectives_count += 1
        on_track_keyresults_set = objective.keyresults_set
        if on_track_keyresults_set.count():
            on_track_keyresults = on_track_keyresults_set.filter(
                                Q(updated_date__gte=filter_date) &
                                ~Q(status="Complete"))
            if not on_track_keyresults:
                on_track_objectives += 1
    return (on_track_objectives, objectives_count)

def _get_updated_objectives(
        updated_date, objectives_count=0, 
        updated_objectives=0):
    """
    Function to get the objectives count and on updated objectives after updated_date
    Args:
        updated_date - date after which the objectives count and updated objectives
                       to be retreived
    Returns:
        objectives_count - total objectives count
        on_track_objectives - updated  objectives count after updated_date
    """
    for objective in Objectives.objects.all():
        objectives_count += 1
        updated_keyresults_set = objective.keyresults_set
        if updated_keyresults_set.count():
            updated_keyresults = updated_keyresults_set.filter(
                               updated_date__gte=updated_date)
            if updated_keyresults:
                updated_objectives += 1
    return (updated_objectives, objectives_count)

def _get_updated_objectives_bw_dates(
        start_date, end_date, objectives_count=0, 
        updated_objectives=0):
    """
    Function to get the objectives count and on updated objectives between the dates
    Args:
        start_date - date from which the updated objectives count to be retrieved
        end_date - date to which the updated objectives count to be retrieved
    Returns:
        objectives_count - total objectives count
        on_track_objectives - updated  objectives count between the dates.
    """
    for objective in Objectives.objects.all():
        objectives_count += 1
        updated_keyresults_set = objective.keyresults_set
        if updated_keyresults_set.count():
            updated_keyresults = updated_keyresults_set.filter(
                               Q(updated_date__gte=start_date) &
                               Q(updated_date__lte=end_date))
            if updated_keyresults:
                updated_objectives += 1
    return (updated_objectives, objectives_count)

def get_teams(request):
    """
    Rest endpoint to get teams and info for a department
    Returns(HTTP response):
    django_context variable
    {

        "teams": [
            {
                "team_leader": "Kailash", 
                "members": ["Preetam", "Rekha"]
            },
            {
                "team_leader": "Johnson", 
                "members": ["Haris", "Ashok"]
            }
        ],
        "department": "Product"
    }
    """
    if request.method == "GET":
        try:
            department_name = request.GET.get("department_name", None)
            logger.info("Recieved request to fetch all the teams for the "
                        "department: %s" % department_name)
            teams = _get_teams_for_dept(department_name)
            resp = {
                "department": department_name,
                "teams": teams
            }
            logger.info("Output response for all the teams of a "
                        "department is: %s" % str(resp))
            return render(request, 'teams.html', resp)
        except Exception as err:
            logger.error("Error retrieving teams for department: %s, Error: %s,"
                         " Stack: %s" % (department_name, str(err), format_exc()))
    return render(request, 'error.html')

def _get_teams_for_dept(dept_name):
    """
    Function to return the team details for a department
    Args:
        dept_name = department name
    Returns:
        [
            {
                "team_leader": "Kailash", 
                "members": ["Preetam", "Rekha"]
            },
            {
                "team_leader": "Johnson", 
                "members": ["Haris", "Ashok"]
            }
        ]
    """
    dept = Department.objects.filter(name__iexact=dept_name)
    all_teams = []
    if dept:
        dept = dept[0]
        teams = dept.teams_set.all()
        for team in teams:
            team_details = {}
            team_details["team_leader"] = team.team_lead_id.first_name
            team_members = list(map(lambda x: "%s %s" 
                                              % (x.first_name, x.last_name), 
                                              team.users_set.all()))
            team_lead_full_name = "%s %s" % (team.team_lead_id.first_name, 
                                             team.team_lead_id.last_name)
            if team_lead_full_name in team_members:
                # Remove the team leader from the team members group
                team_members.remove(team_lead_full_name)
            team_details["members"] = team_members
            all_teams.append(team_details)
    return all_teams