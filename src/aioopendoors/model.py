"""Models for Opendoors data."""

from dataclasses import dataclass
from enum import IntEnum, IntFlag

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig


class BatteryLevel(IntEnum):
    """BatteryLevel enum."""

    BATTERY_LEVEL_NORMAL = 0
    BATTERY_LEVEL_ALERT = 1
    BATTERY_LEVEL_CRITICAL = 2


class DoorState(IntEnum):
    """DoorState enum."""

    DOOR_STATE_CLOSE = 0
    DOOR_STATE_OPEN = 1


class LockActionType(IntEnum):
    """LockActionType enum."""

    ACTION_LOCK_UNLOCK = 1
    ACTION_LOCK_LOCK = 2
    ACTION_LOCK_SYNC = 3
    ACTION_LOCK_FORCE_LOCK = 9


class LockActionState(IntEnum):
    """LockActionState enum."""

    ACTION_STATE_PENDING = 0
    ACTION_STATE_ONHOLD = 1
    ACTION_STATE_SUCCESS = 2
    ACTION_STATE_FAILURE = 3


class LockState(IntFlag):
    """LockState flag."""

    INIT_REQUIRED = 1
    SYNC_REQUIRED = 2
    SYNC_READER = 4
    UNKNOWN = 8
    LOCKED = 16
    UNLOCKED = 32
    GATEWAY_RANGE = 64


@dataclass
class LockActionStatus(DataClassDictMixin):
    """DataClass for LockActionStatus."""

    action_type: LockActionType
    action_state: LockActionState

    class Config(BaseConfig):
        """ConfigClass for LockActionStatus dictionary."""

        aliases = {
            "action_type": "ACTION_TYPE",
            "action_state": "ACTION_STATE",
        }


@dataclass
class LockAction(LockActionStatus):
    """DataClass for LockAction."""

    id: str

    class Config(BaseConfig):
        """ConfigClass for LockAction dictionary."""

        aliases = {
            "id": "ACTION_UID",
            "action_type": "ACTION_TYPE",
            "action_state": "ACTION_STATE",
        }


@dataclass
class LockStatus(DataClassDictMixin):
    """DataClass for LockStatus."""

    errors: list[str] | None
    site_id: str
    uid: str
    state: LockState
    door_state: DoorState
    download_update: bool
    serial_number: str

    class Config(BaseConfig):
        """ConfigClass for LockStatus dictionary."""

        aliases = {
            "errors": "ERRORS",
            "site_id": "DEVICE_SITEID",
            "uid": "DEVICE_UID",
            "state": "ACTUATOR_STATE",
            "door_state": "ACTUATOR_DOOR_STATE",
            "download_update": "DOWNLOAD_UPDATE",
            "serial_number": "DEVICE_OCSN",
        }


@dataclass
class LockAttributes(LockStatus):
    """DataClass for LockAttributes values."""

    type: int
    name: str
    timezone: str
    country_code: str
    timezone_offset: int
    group_name: str
    reader: str | None
    auto_lock: int
    lock_keepopen_timeout: int | None
    battery_level: BatteryLevel
    door_state: DoorState
    leave_n_go: int
    direct_lock: int
    direct_unlock: int
    night_mode: int
    start_night_mode: str
    end_night_mode: str
    open_door_alarm: int
    breakin_alarm: int
    lock_pick_alarm: int
    auto_armed: bool
    auto_disarmed: bool
    tof_sensor: bool
    last_sync_done: str
    is_sub_admin: bool
    has_access_gateway: bool
    firmware_version: str
    protect_armed: bool
    linked_gateway: bool
    action: LockAction | None = None

    class Config(BaseConfig):
        """ConfigClass for LockAttributes dictionary."""

        omit_default = True
        aliases = {
            "errors": "ERRORS",
            "site_id": "DEVICE_SITEID",
            "uid": "DEVICE_UID",
            "state": "ACTUATOR_STATE",
            "door_state": "ACTUATOR_DOOR_STATE",
            "download_update": "DOWNLOAD_UPDATE",
            "serial_number": "DEVICE_OCSN",
            "type": "DEVICE_TYPE",
            "name": "ACTUATOR_NAME",
            "timezone": "ACTUATOR_TZ",
            "country_code": "ACTUATOR_CC",
            "timezone_offset": "ACTUATOR_TZ_OFFSET",
            "group_name": "ACTUATOR_GROUP_NAME",
            "reader": "ACTUATOR_READER",
            "auto_lock": "ACTUATOR_AUTO_LOCK",
            "lock_keepopen_timeout": "_LOCK_KEEPOPEN_TIMEOUT",
            "battery_level": "ACTUATOR_BATTERYLEVEL",
            "leave_n_go": "ACTUATOR_LEAVE_N_GO",
            "direct_lock": "ACTUATOR_DIRECT_LOCK",
            "direct_unlock": "ACTUATOR_DIRECT_UNLOCK",
            "night_mode": "ACTUATOR_NIGHT_MODE",
            "start_night_mode": "ACTUATOR_START_NIGHT_MODE",
            "end_night_mode": "ACTUATOR_END_NIGHT_MODE",
            "open_door_alarm": "ACTUATOR_OPEN_DOOR_ALARM",
            "breakin_alarm": "ACTUATOR_BREAKIN_ALARM",
            "lock_pick_alarm": "ACTUATOR_LOCK_PICK_ALARM",
            "auto_armed": "AUTO_ARMED",
            "auto_disarmed": "AUTO_DISARMED",
            "tof_sensor": "TOF_SENSOR",
            "has_access_gateway": "HAS_ACCESS_GATEWAY",
            "last_sync_done": "_LASTSYNCDONE",
            "is_sub_admin": "IS_SUB_ADMIN",
            "firmware_version": "FIRMWARE_VERSION",
            "protect_armed": "PROTECT_ARMED",
            "linked_gateway": "_LINKED_GATEWAY",
        }
