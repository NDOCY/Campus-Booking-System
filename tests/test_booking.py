import pytest
from datetime import datetime
from models.models import User, Facility, Booking, UserRole

@pytest.fixture
def user(session):
    u = User(username="tester", email="tester@example.com", password_hash="hash", role=UserRole.student)
    session.add(u)
    session.commit()
    return u

@pytest.fixture
def facility(session):
    f = Facility(name="Test Room", type="lab", capacity=10)
    session.add(f)
    session.commit()
    return f

def test_overlap_prevention(session, user, facility):
    """Booking that overlaps mid-way through an existing booking should be rejected."""
    start1 = datetime(2026, 5, 1, 10, 0, 0)
    end1   = datetime(2026, 5, 1, 12, 0, 0)
    b1 = Booking(user_id=user.user_id, facility_id=facility.facility_id,
                 start_time=start1, end_time=end1, purpose="First")
    session.add(b1)
    session.commit()

    # Starts during the first booking
    start2 = datetime(2026, 5, 1, 11, 0, 0)
    end2   = datetime(2026, 5, 1, 13, 0, 0)
    b2 = Booking(user_id=user.user_id, facility_id=facility.facility_id,
                 start_time=start2, end_time=end2, purpose="Second")
    session.add(b2)

    with pytest.raises(ValueError, match="Booking conflict"):
        session.commit()

def test_boundary_touching_allowed(session, user, facility):
    """A booking that starts exactly when another ends should be allowed (no overlap)."""
    start1 = datetime(2026, 5, 1, 10, 0, 0)
    end1   = datetime(2026, 5, 1, 12, 0, 0)
    b1 = Booking(user_id=user.user_id, facility_id=facility.facility_id,
                 start_time=start1, end_time=end1, purpose="First")
    session.add(b1)
    session.commit()

    # Starts exactly when the first one ends — should be fine
    start2 = datetime(2026, 5, 1, 12, 0, 0)
    end2   = datetime(2026, 5, 1, 14, 0, 0)
    b2 = Booking(user_id=user.user_id, facility_id=facility.facility_id,
                 start_time=start2, end_time=end2, purpose="Second")
    session.add(b2)

    session.commit()  # Should NOT raise
    assert b2.booking_id is not None

def test_completely_contained_overlap(session, user, facility):
    """A booking entirely inside an existing booking should be rejected."""
    start1 = datetime(2026, 5, 1, 9, 0, 0)
    end1   = datetime(2026, 5, 1, 17, 0, 0)
    b1 = Booking(user_id=user.user_id, facility_id=facility.facility_id,
                 start_time=start1, end_time=end1, purpose="Full day")
    session.add(b1)
    session.commit()

    # Entirely within the first booking
    start2 = datetime(2026, 5, 1, 11, 0, 0)
    end2   = datetime(2026, 5, 1, 13, 0, 0)
    b2 = Booking(user_id=user.user_id, facility_id=facility.facility_id,
                 start_time=start2, end_time=end2, purpose="Nested")
    session.add(b2)

    with pytest.raises(ValueError, match="Booking conflict"):
        session.commit()

def test_different_facility_no_conflict(session, user, facility):
    """Same time slot on a different facility should be allowed."""
    other = Facility(name="Other Room", type="lab", capacity=10)
    session.add(other)
    session.commit()

    start = datetime(2026, 5, 1, 10, 0, 0)
    end   = datetime(2026, 5, 1, 12, 0, 0)

    b1 = Booking(user_id=user.user_id, facility_id=facility.facility_id,
                 start_time=start, end_time=end, purpose="Room 1")
    session.add(b1)
    session.commit()

    b2 = Booking(user_id=user.user_id, facility_id=other.facility_id,
                 start_time=start, end_time=end, purpose="Room 2")
    session.add(b2)

    session.commit()  # Should NOT raise
    assert b2.booking_id is not None
