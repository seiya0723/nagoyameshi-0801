from django.contrib import admin

# Register your models here.
# admin.pyは管理サイトで操作したいモデルを登録する係。
# admin.py は models.py の中の Category,Restaurant,Review,Favorite,Reservation,PremiumUser をimportする。

# admin.py se encarga de registrar el modelo que desea operar en el sitio de administración.
# admin.py importa Categoría, Restaurante, Reseña, Favorito, Reserva, Usuario Premium en models.py.

from .models import Category,Restaurant,Review,Favorite,Reservation,PremiumUser

# 管理サイトに登録をする。
# Regístros en el sitio de administración.

admin.site.register(Category)
admin.site.register(Restaurant)
admin.site.register(Review)
admin.site.register(Favorite)
admin.site.register(Reservation)
admin.site.register(PremiumUser)
