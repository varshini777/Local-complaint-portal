from backend.models import User, Ward, ComplaintCategory


def populate_officer_choices(form):
    """Populate officer choices in a form."""
    officers = User.query.filter_by(role=User.ROLE_OFFICER, is_active=True).order_by(User.full_name).all()
    form.assigned_officer_id.choices = [(0, "Unassigned")] + [(o.user_id, o.full_name) for o in officers]


def populate_ward_choices(form):
    """Populate ward choices in a form."""
    wards = Ward.query.order_by(Ward.ward_name).all()
    form.ward_id.choices = [(0, "All Wards")] + [(w.ward_id, w.ward_name) for w in wards]


def populate_category_choices(form):
    """Populate category choices in a form."""
    categories = ComplaintCategory.query.order_by(ComplaintCategory.category_name).all()
    form.category_id.choices = [(0, "All Categories")] + [(c.category_id, c.category_name) for c in categories]


def populate_active_category_choices(form):
    """Populate active category choices for complaint submission."""
    categories = ComplaintCategory.query.filter_by(is_active=True).order_by(ComplaintCategory.category_name).all()
    form.category.choices = [(category.category_id, category.category_name) for category in categories]


def populate_active_ward_choices(form):
    """Populate active ward choices for complaint submission."""
    wards = Ward.query.filter_by(is_active=True).order_by(Ward.ward_name).all()
    form.ward.choices = [(ward.ward_id, ward.display_name) for ward in wards]
