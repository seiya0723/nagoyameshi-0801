from django import forms 

# Reviewを元にバリデーションルールを作る
# Crear reglas de validación basadas en reseñas
from .models import Review,Favorite,Reservation

class ReviewForm(forms.ModelForm):
    class Meta:
        model   = Review
        fields  = ["user","restaurant","content"]

# Favoriteを元にバリデーションルールを作る
# Crear reglas de validación basadas en Favoritos
class FavoriteForm(forms.ModelForm):
    class Meta:
        model   = Favorite
        fields  = ["user","restaurant"]


class ReservationForm(forms.ModelForm):
    class Meta:
        model   = Reservation
        fields  = ["user","restaurant", "datetime","headcount"]




"""
from .models import Topic

# Topicモデルを元にして作ったバリデーションルール(フォームクラス)
class TopicForm(forms.ModelForm):

    class Meta:
        model   = Topic
        fields  = [ "comment" ]
"""