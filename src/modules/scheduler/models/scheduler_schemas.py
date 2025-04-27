# Id: scheduler_schemas.py 202307 18/07/2023
#
# backend
# Copyright (c) 2011-2013 IntegraSoft S.R.L. All rights reserved.
#
# Author: cicada
#   Rev: 202307
#   Date: 18/07/2023
#
# License description...
from datetime import datetime, date
import pytz
from pydantic import Field, constr, field_validator, ValidationError
from typing import Literal
from project_helpers.schemas import BaseSchema
from apscheduler.triggers.cron import CronTrigger


class SchedulerBody(BaseSchema):
    jobName: str = Field(..., example="manual_start_example_job")
    dayOfWeek: constr(pattern=r"^(mon|tue|wed|thu|fri|sat|sun|\*)(,(mon|tue|wed|thu|fri|sat|sun|\*))*$") = Field(
        "*", example="mon,tue"
    )
    hour: constr(pattern=r"^(?:[0-1]?[0-9]|2[0-3]|\*)$") = Field("*", example="12")
    minute: constr(pattern=r"^(?:[0-5]?[0-9]|\*)$") = Field("*", example="12")
    timezone: str = Field("Europe/Bucharest", example="Europe/Berlin")
    startDate: date = Field(None, example="2023-06-20", format="%Y-%m-%d")
    endDate: date = Field(None, example="2023-06-20", format="%Y-%m-%d")
    trigger: Literal["cron", "interval"] = "cron"
    frequencyUnit: Literal["seconds", "minutes", "hours", "days"] = "seconds"
    frequencyValue: int = None

    @field_validator("timezone")
    def validate_timezone(cls, value):
        if value not in pytz.all_timezones:
            raise ValidationError(f"Timezone must be one of: {pytz.all_timezones}")


class SchedulerResponse(BaseSchema):
    id: str
    dayOfWeek: constr(pattern=r"^(mon|tue|wed|thu|fri|sat|sun|\*)(,(mon|tue|wed|thu|fri|sat|sun|\*))*$") = Field(
        None, example="mon,tue"
    )
    hour: constr(pattern=r"^(?:[0-1]?[0-9]|2[0-3]|\*)$") = Field("*", example="12")
    minute: constr(pattern=r"^(?:[0-5]?[0-9]|\*)$") = Field("*", example="12")
    timezone: str = Field(None, example="Europe/Berlin")
    startDate: date = Field(None, example="2023-06-20", format="%Y-%m-%d")
    endDate: date = Field(None, example="2023-06-20", format="%Y-%m-%d")
    trigger: Literal["cron", "interval"] = Field(None, example="cron")
    frequencyUnit: Literal["seconds", "minutes", "hours", "days"] = Field(None, example="cron")
    frequencyValue: int = Field(None, example=5)
    jobName: str = Field(..., example="manual_start_example_job")
    nextRunTime: datetime = Field(None, example="2023-12-12 18:05", format="%Y-%m-%d %H:%M")

    @classmethod
    def from_job(cls, job):
        data = dict()
        timezone = None
        triggerValue = "interval"
        trigger = job.trigger
        frequencyUnit = None
        frequencyValue = None
        if isinstance(job.trigger, CronTrigger):
            triggerValue = "cron"
            timezone = trigger.timezone and str(trigger.timezone) or None
            data = {f.name: str(f) for f in trigger.fields}
        else:
            frequencyUnit = (
                hasattr(trigger.interval, "seconds")
                and "seconds"
                or hasattr(trigger.interval, "minutes")
                and "minutes"
                or hasattr(trigger.interval, "hours")
                and "hours"
                or hasattr(trigger.interval, "days")
                and "days"
            )
            frequencyValue = getattr(trigger.interval, frequencyUnit)

        return cls(
            id=job.id,
            dayOfWeek=(
                data.get("day_of_week", None) if data.get("day_of_week") != "*" else "mon,tue,wed,thu,fri,sat,sun"
            ),
            hour=data.get("hour", None),
            timezone=timezone,
            minute=data.get("minute", None),
            trigger=triggerValue,
            startDate=trigger.start_date,
            endDate=trigger.end_date,
            frequencyUnit=frequencyUnit,
            frequencyValue=frequencyValue,
            nextRunTime=job.next_run_time,
            jobName=job.name,
        )
