from django.forms import Form, ChoiceField, IntegerField
from .neo4j_utils import R_category

categories = (
    ('r', "Random"),
    ('a', "Actor"),
    ('g', "Genre"),
    ('u', "User"),
)

class RecommendationForm(Form):
    category = ChoiceField(choices=categories)
    number = IntegerField(min_value=1, max_value=5)