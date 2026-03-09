from database import SessionLocal
from models.models import User, Facility, Booking, Notification, UserRole, BookingStatus
from datetime import datetime
import bcrypt

def hash_password(plain_text: str) -> str:
    return bcrypt.hashpw(plain_text.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

db = SessionLocal()

# Add users — passwords are properly hashed with bcrypt
user1 = User(username="alice", email="alice@university.edu",
             password_hash=hash_password("StudentPass1!"), role=UserRole.student)
user2 = User(username="bob", email="bob@university.edu",
             password_hash=hash_password("StaffPass2!"), role=UserRole.staff)   # was 'lecturer'
admin = User(username="carol", email="carol@university.edu",
             password_hash=hash_password("AdminPass3!"), role=UserRole.admin)

db.add_all([user1, user2, admin])
db.commit()

# Add facilities
lab = Facility(name="Lab 101", type="lab", capacity=30, description="Computer lab")
hall = Facility(name="Main Hall", type="hall", capacity=200, description="Auditorium")
court = Facility(name="Tennis Court", type="sports", capacity=4, description="Outdoor court")

db.add_all([lab, hall, court])
db.commit()

# Add a booking (pending)
booking = Booking(
    facility_id=lab.facility_id,
    user_id=user1.user_id,
    start_time=datetime(2026, 4, 10, 9, 0),
    end_time=datetime(2026, 4, 10, 11, 0),
    purpose="Database lab session",
    status=BookingStatus.pending
)
db.add(booking)
db.commit()

# Add a notification
notif = Notification(
    user_id=user1.user_id,
    booking_id=booking.booking_id,
    message="Your booking for Lab 101 has been received and is awaiting approval.",
    channel="email"
)
db.add(notif)
db.commit()

print("✅ Sample data inserted!")
db.close()
