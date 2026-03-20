"""
Database initialization and seeding functions.
"""
from sqlalchemy.orm import Session
from app.db.models import Role, User
from app.core.security import hash_password


def init_roles(db: Session) -> None:
    """Initialize default roles if they don't exist."""
    roles = ["admin", "faculty", "student"]
    role_descriptions = {
        "admin": "Administrator with full system access",
        "faculty": "Faculty member who teaches courses",
        "student": "Student enrolled in courses",
    }
    
    for role_name in roles:
        existing = db.query(Role).filter(Role.name == role_name).first()
        if not existing:
            role = Role(
                name=role_name,
                description=role_descriptions.get(role_name, ""),
            )
            db.add(role)
    db.commit()


def init_admin_user(db: Session) -> None:
    """Create default admin user if it doesn't exist."""
    admin_email = "admin@college.edu"
    existing_admin = db.query(User).filter(User.email == admin_email).first()
    
    if not existing_admin:
        # Ensure admin role exists first
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator with full system access")
            db.add(admin_role)
            db.commit()
        
        # Create admin user
        admin_user = User(
            email=admin_email,
            full_name="Administrator",
            hashed_password=hash_password("admin123"),
            role_id=admin_role.id,
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        print(f"✓ Admin user created: {admin_email} / admin123")
    else:
        print(f"✓ Admin user already exists: {admin_email}")


def seed_database(db: Session) -> None:
    """Run all seeding functions."""
    print("🌱 Seeding database...")
    init_roles(db)
    init_admin_user(db)
    print("✓ Database seeding complete!")
