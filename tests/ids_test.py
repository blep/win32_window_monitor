import pytest
from win32_window_monitor.ids import HookEvent, ObjectId


# HookEvent and indirectly test NamedInt
# ###################################################################


def test_event_constant_is_event_type():
    assert type(HookEvent.AIA_START) == HookEvent


def test_event_constant_are_subclass_of_int():
    assert isinstance(HookEvent.AIA_START, int)


def test_event_convertible_to_int():
    assert int(HookEvent.AIA_START) == 0xA000
    assert int(HookEvent.AIA_START) != 0xA001


def test_event_from_unknown_int():
    assert isinstance(HookEvent(0x1234), HookEvent)
    assert HookEvent(0x1234) == 0x1234


def test_event_value_error_if_not_int():
    with pytest.raises(ValueError, match="expected value to be a int, but was 'not a int'"):
        HookEvent('not a int')


def test_event_name():
    assert HookEvent.AIA_START.name == 'AIA_START'
    assert HookEvent(1234).name is None


def test_event_value():
    assert HookEvent.AIA_START.value == 0xA000
    assert HookEvent(1234).value == 1234


def test_event_repr():
    assert repr(HookEvent.AIA_START) == 'HookEvent.AIA_START'
    assert repr(HookEvent(0x1234)) == 'HookEvent(0x1234)'


def test_event_str():
    assert str(HookEvent.AIA_START) == 'AIA_START'
    assert str(HookEvent(0x1234)) == '0x1234'


def test_convert_int_to_named_event():
    assert type(HookEvent(0xA000)) == HookEvent
    assert HookEvent(0xA000) == HookEvent.AIA_START


def test_event_names():
    names = list(HookEvent.names())
    assert len(names) > 1
    assert HookEvent.AIA_START.name in names


def test_event_values():
    values = list(HookEvent.values())
    assert len(values) > 1
    assert type(values[0]) == HookEvent
    assert HookEvent.AIA_START in values


def test_event_eq():
    assert HookEvent.AIA_START == HookEvent.AIA_START
    assert not (HookEvent.AIA_START == HookEvent.AIA_END)
    assert HookEvent.AIA_START != HookEvent.AIA_END
    assert HookEvent.AIA_START == HookEvent(0xa000)
    assert HookEvent.AIA_START == 0xa000
    assert 0xa000 == HookEvent.AIA_START


def test_event_cmp():
    assert HookEvent.AIA_START < HookEvent.AIA_END
    assert HookEvent.AIA_END > HookEvent.AIA_START
    assert HookEvent.AIA_END >= HookEvent.AIA_START


def test_event_hashable():
    assert hash(HookEvent.AIA_START) == hash(HookEvent.AIA_START.value)


# ObjectId
# ###################################################################

def test_objid_repr():
    assert repr(ObjectId.CURSOR) == 'ObjectId.CURSOR'
    assert repr(ObjectId(0x1234)) == 'ObjectId(0x1234)'


def test_objid_str():
    assert str(ObjectId.CURSOR) == 'CURSOR'
    assert str(ObjectId(0x1234)) == '0x1234'


def test_convert_int_to_named_objid():
    assert type(ObjectId(0xFFFFFFF7)) == ObjectId
    assert ObjectId(0xFFFFFFF7) == ObjectId.CURSOR


def test_objid_eq():
    assert ObjectId.CURSOR == ObjectId.CURSOR
    assert ObjectId.CURSOR != ObjectId.WINDOW
    assert ObjectId.CURSOR == ObjectId(0xFFFFFFF7)
    assert ObjectId.CURSOR == 0xFFFFFFF7
    assert 0xFFFFFFF7 == ObjectId.CURSOR
