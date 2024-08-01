from django.urls import path

# views.pyをimportする。
from nagoyameshi import views



app_name    = "nagoyameshi"
urlpatterns = [
    path("", views.index, name="index"),
    path("restaurant/<int:pk>/", views.restaurant, name="restaurant" ),
    #             ↑ <int:pk> は int型(整数型)の場合、整数をpkとして扱う。このpkをビューに引き渡す。
    # restaurant/1/ や restaurant/3/ 
    path("review/", views.review, name="review"),
    path("favorite/", views.favorite, name="favorite"),
    path("reservation/",views.reservation, name="reservation"),
    
    path("mypage/", views.mypage, name="mypage"),
  
    # レビューの削除と編集を追加する。
    path("review_edit/<int:pk>/", views.review_edit, name="review_edit" ),
    path("review_delete/<int:pk>/", views.review_delete, name="review_delete" ),


    # 予約キャンセルのURL設定を追加
    path("reservation_cancel/<int:pk>/", views.reservation_cancel, name="reservation_cancel" ),

    # Stripeのセッションを作る checkout 
    path("checkout/", views.checkout, name="checkout"),
    
    # Stripeのセッション(支払い)を確認する success
    path("success/", views.success, name="success"),

    # サブスクリプションの操作
    path("portal/", views.portal, name="portal"),


]
