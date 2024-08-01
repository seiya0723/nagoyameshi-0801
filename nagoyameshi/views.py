from django.shortcuts import render, redirect

from django.views import View

# クエリビルダ
from django.db.models import Q


# models.py の中の Restaurant クラスをimportするには？
#from .models import Restaurant

# models.py の中の Category クラスをimportするには？
#from .models import Category

# ↑2つは ↓ 1つで書ける
from .models import Restaurant, Category, Review, Favorite, Reservation, PremiumUser

# forms.pyから ReviewFormをimportする。
from .forms import ReviewForm,FavoriteForm,ReservationForm


# トップページで一覧表示をするビュー
# index.htmlをレンダリングするビューを作る

# ビューに多重継承させることで、ログイン状態をチェックして、未ログインであればログインページ( accounts/login/ )へリダイレクトできる。
from django.contrib.auth.mixins import LoginRequiredMixin

from django.utils import timezone


# == stripe ==
# settings.pyを読み込み
from django.conf import settings
# URLを作る。
from django.urls import reverse_lazy

# pip install stripe 
import stripe
# settings.pyのAPIキーをセットする。
stripe.api_key  = settings.STRIPE_API_KEY

# 2: Stripeにセッションを作ってもらう
# Stripeに対してセッションを作ってくれと依頼をするビュー。
class CheckoutView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):

        #  ↓3: セッションを作った   ↓ 2: セッションを作る
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': settings.STRIPE_PRICE_ID,
                    'quantity': 1,
                },
            ],
            payment_method_types=['card'],
            mode='subscription',

            # 6 で Stripeがカードで支払い成功したときのURL。クライアントがカードを入力せずにキャンセルしたときのURL
            success_url=request.build_absolute_uri(reverse_lazy("nagoyameshi:success")) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse_lazy("nagoyameshi:mypage")),
            # 絶対パスのURLを作っている。 http から始まるURL
        )

        # セッションid
        print( checkout_session["id"] )

        # 4: 作ったセッションのURLヘリダイレクトする。
        return redirect(checkout_session.url)

checkout    = CheckoutView.as_view()


# 5: クライアントはStripeのサイトへ行き、カードを入力
# 6: Stripeはカードで支払い

# 7: Stripeは↓のビューへリダイレクト
class SuccessView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):


        # 8: DjangoはStripeへカードの支払いを確認する。

        # パラメータにセッションIDがあるかチェック
        if "session_id" not in request.GET:
            print("セッションIDがありません。")
            return redirect("nagoyameshi:index")


        # そのセッションIDは有効であるかチェック。
        try:
            checkout_session_id = request.GET['session_id']
            checkout_session    = stripe.checkout.Session.retrieve(checkout_session_id)
        except:
            print( "このセッションIDは無効です。")
            return redirect("nagoyameshi:index")

        print(checkout_session)

        # statusをチェックする。未払であれば拒否する。(未払いのsession_idを入れられたときの対策)
        if checkout_session["payment_status"] != "paid":
            print("未払い")
            return redirect("nagoyameshi:index")

        print("支払い済み")


        # 有効であれば、セッションIDからカスタマーIDを取得。ユーザーモデルへカスタマーIDを記録する。
        """
        request.user.customer   = checkout_session["customer"]
        request.user.save()
        """

        # PremiumUser を新規作成する。
        premium_user        = PremiumUser()
        premium_user.user   = request.user
        premium_user.premium_code = checkout_session["customer"]

        premium_user.save()

        print("有料会員登録しました！")

        return redirect("nagoyameshi:mypage")

success     = SuccessView.as_view()



# サブスクリプションの操作関係
class PortalView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        
        premium_user = PremiumUser.objects.filter(user=request.user).first()

        if not premium_user:
            print( "有料会員登録されていません")
            return redirect("nagoyameshi:index")

        # ユーザーモデルに記録しているカスタマーIDを使って、ポータルサイトへリダイレクト
        portalSession   = stripe.billing_portal.Session.create(
            customer    = premium_user.premium_code,
            return_url  = request.build_absolute_uri(reverse_lazy("nagoyameshi:index")),
        )

        return redirect(portalSession.url)

portal = PortalView.as_view()





# == stripe ==





class IndexView(View):

    def get(self, request, *args, **kwargs):
    
        context = {}

        # 検索フォームに、カテゴリの選択肢を作るためにも、カテゴリの全データを取り出す。
        context["categories"]   = Category.objects.all()



        #クエリを初期化しておく。
        query   = Q() 
        # この時点では検索の条件が何もない。
        # なので、 Restaurant.objects.filter(query) = Restaurant.objects.all()

        # query に検索条件を加え ↓のようにfilterの引数として使う。
        #  Restaurant.objects.filter(query)





        #検索キーワードがある場合のみ取り出す
        if "search" in request.GET:
            
            # "　A　洋食" → " A 洋食" → ["","A","洋食"]
            # "洋食　A" → "洋食 A" → [ "洋食","A" ]
            #全角スペースを半角スペースに変換、スペース区切りでリストにする。
            words   = request.GET["search"].replace("　"," ").split(" ")

            #クエリを追加する
            for word in words:

                #空欄の場合は次のループへ
                if word == "": 
                    continue

                #TIPS:AND検索の場合は&を、OR検索の場合は|を使用する。
                #query &= Q(comment__contains=word)
                query &= Q(name__contains=word)
                # 最初は query の条件は空
                # 1回目のループで、 query &= Q(name__contains="洋食")
                # 2回目のループで、 query &= Q(name__contains="A")
                # 2回目のループが終わった時点の query は？  Restaurantのnameに、『洋食を含んでいる』なおかつ『Aを含んでいる』
        """
            # 作った条件を使って検索する。
            context["restaurants"] = Restaurant.objects.filter(query)
        else:
            # 全件出す。
            context["restaurants"] = Restaurant.objects.all()
            # この時点ではqueryは空の状態
            context["restaurants"] = Restaurant.objects.filter(query)
        """

        # TODO: カテゴリ検索をする。

        if "category" in request.GET:
            if request.GET["category"] != "":
                query &= Q(category=request.GET["category"])



        # 検索している場合もしていない場合も、Restaurant.objects.filter(query) でOK
        #作ったクエリを実行(検索のパラメータがない場合、絞り込みは発動しない。)
        #context["topics"] = Topic.objects.filter(query)
        context["restaurants"] = Restaurant.objects.filter(query)
        



        #return render(request,"bbs/index.html",context)
        return render(request,"nagoyameshi/index.html",context)

# urls.pyから呼び出せるようにする
index   = IndexView.as_view()


# 店舗の個別ページを表示させるビュー
class RestaurantView(View):
    def get(self, request, pk, *args, **kwargs):
        context = {}

        # URLに含まれている整数がここで扱える。
        print(pk)

        # 店舗の個別ページなので pk( Restaurantのid)  を使って店舗検索をする。
        # .filter() で終わると、配列になってしまう。1個しかないのに配列になる。
        # .first() 配列から1番最初の要素を取る。
        context["restaurant"]   = Restaurant.objects.filter(id=pk).first()



        # レビューの全データを取り出す。全データのリスト。
        # FIXME: これでは、全店舗のレビューが表示されてしまう。
        # context["reviews"]   = Review.objects.all()
        
        # 表示する店舗に紐づくレビューだけを取る。
        context["reviews"]   = Review.objects.filter(restaurant=pk)


        # この店舗をお気に入りしたデータを全て取り出す。
        # Favorite.objects.filter(restaurant=pk)

        # 自分がお気に入りしているか？
        if request.user.is_authenticated:
            # request.userがNoneになってしまう。Noneで検索ができない。
            context["is_favorite"]   = Favorite.objects.filter(restaurant=pk,user=request.user)
        else:
            context["is_favorite"]   = False
        

        return render(request, "nagoyameshi/restaurant.html", context)

restaurant = RestaurantView.as_view()

class ReviewView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        
        #TODO: Reviewの投稿処理をする。
        print("投稿処理をする")

        #TODO: ReviewFormを使って、チェックをした上で、DBに保存する。
        form    = ReviewForm(request.POST)

        # .is_valid()でルールに従っているかチェックする。
        if form.is_valid():
            print("保存")
            form.save()
        else:
            print(form.errors)


        #TODO: 投稿処理を終えた後、トップページに移動
        # "app_name:name" で移動先のURLを与える
        return redirect("nagoyameshi:index")

review = ReviewView.as_view()


# TODO: レビューの編集をするビュー

class ReviewEditView(LoginRequiredMixin, View):

    # 編集画面を表示する
    def get(self, request, pk, *args, **kwargs):
        
        # TODO:編集するレビューを特定。
        context = {}

        # 編集する1件分のデータを特定する。1件しか無いが、これだとリスト型になってしまう。.first() 
        context["review"] = Review.objects.filter(id=pk, user=request.user).first()


        # 編集画面のページ(編集のフォーム)を表示する。 review_edit.html 
        return render(request, "nagoyameshi/review_edit.html",context)

    # 編集処理を受け付ける。
    #                       ↓ 編集したいReviewのid 
    def post(self, request, pk, *args, **kwargs):
        
        # TIPS: .filter() で終わると、結果が1件だけでもリストで出てくるので、.first() を使う。
        review = Review.objects.filter(id=pk, user=request.user).first()
        print("編集")


        # TODO: 編集処理をする。
        # バリデーションをする。ただし、編集をする場合、instance引数に編集対象のデータを指定。
        form    = ReviewForm(request.POST, instance=review)

        # instanceがないと、新規作成になってしまう。
        #form    = ReviewForm(request.POST)

        # .is_valid()でルールに従っているかチェックする。
        if form.is_valid():
            print("保存")
            form.save()
        else:
            print(form.errors)



        # 店舗の個別ページにリダイレクトさせるには？ 店舗のidが必要。reviewから取り出す。
        return redirect("nagoyameshi:restaurant", review.restaurant.id )

review_edit = ReviewEditView.as_view()

# TODO: レビューの削除をするビュー
class ReviewDeleteView(LoginRequiredMixin, View):
    #                       ↓ 削除したいReviewのid 
    def post(self, request, pk, *args, **kwargs):

        # pkを使って、Reviewから削除したいデータを取り出すには？
        # review = Review.objects.filter(id=pk)
        # ↑だと、自分が投稿していないレビューまで削除できるので、ユーザーでも絞り込みをする。
        review = Review.objects.filter(id=pk, user=request.user)

        # 削除する。
        review.delete()


        return redirect("nagoyameshi:index")

review_delete = ReviewDeleteView.as_view()




class FavoriteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        
        # TODO: ↓ と同じものをレビューと予約の冒頭に入れる。

        # ===== リクエストを送ったユーザーが有料会員登録をしているかチェックをする =====

        premium_user = PremiumUser.objects.filter(user=request.user).first()
        
        # このカスタマーidを使って、サブスクリプションが有効かチェックをする。
        #premium_user.premium_code 

        # PremiumUserにデータがなかった場合(まだ有料会員登録をしていない状態)        
        if not premium_user:
            print("カスタマーIDがセットされていません。")
            return redirect("nagoyameshi:index")


        # カスタマーIDを元にStripeに問い合わせ
        try:
            subscriptions = stripe.Subscription.list(customer=premium_user.premium_code )
        except:
            print("このカスタマーIDは無効です。")
            premium_user.delete()

            return redirect("nagoyameshi:index")


        premium = False
        # ステータスがアクティブであるかチェック。
        for subscription in subscriptions.auto_paging_iter():
            if subscription.status == "active":
                print("サブスクリプションは有効です。")
                premium = True
            else:
                print("サブスクリプションが無効です。")

        if not premium:
            redirect("nagoyameshi:index")

        # ===== リクエストを送ったユーザーが有料会員登録をしているかチェックをする =====










        #TODO:お気に入りの登録処理をする。Procesar el registro de favoritos.


        #TODO: FavoriteFormを使って、チェックをした上で、DBに保存する。
        #TODO: Utilice FavoriteForm para comprobarlo y guardarlo en la base de datos.

        form    = FavoriteForm(request.POST)

        # .is_valid()でルールに従っているかチェックする。 
        # Compruebe si se siguen las reglas usando .is_valid().
        if form.is_valid():
            print("保存")

            # user と restaurant がもうすでに登録されているかチェックする。
            # .clean() を使うと、 fieldsで指定したuserとrestaurantを含む辞書型が手に入る。
            cleaned = form.clean()
            favorite = Favorite.objects.filter(user=cleaned["user"],restaurant=cleaned["restaurant"])

            if favorite:
                # すでにお気に入りされている場合、.delete() で削除をする
                favorite.delete()
            else:
                form.save()
        else:
            print(form.errors) 


        #TODO: お気に入りの登録を終えた後、トップページに移動
        # "app_name:name" で移動先のURLを与える
        return redirect("nagoyameshi:index")


favorite = FavoriteView.as_view()


class ReservationView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):

        form    = ReservationForm(request.POST)
        if form.is_valid():
            print("保存")
            form.save()
        else:
            print(form.errors)
        return redirect("nagoyameshi:index")
    
reservation = ReservationView.as_view()

#TODO: 予約キャンセルをするビュー

class ReservationCancelView(LoginRequiredMixin, View):
    #                       ↓ 削除(キャンセル)したいReservationのid 
    def post(self, request, pk, *args, **kwargs):

        # 削除したいReservationを特定する。
        #review = Review.objects.filter(id=pk, user=request.user)

        reservation = Reservation.objects.filter(id=pk, user=request.user)
        reservation.delete()

        #TODO: 予約日が未来に限り、削除できる。

        return redirect("nagoyameshi:mypage")

reservation_cancel = ReservationCancelView.as_view()



class MypageView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        # リクエストを送った人の予約・お気に入り・レビューを取り出す。
        context["reviews"]      = Review.objects.filter(user=request.user)
        context["favorites"]    = Favorite.objects.filter(user=request.user)
        context["reservations"] = Reservation.objects.filter(user=request.user)


        # 予約キャンセルのif文に使う今日の日付をcontextに入れる。
        context["now"]          = timezone.now()

        return render(request, "nagoyameshi/mypage.html", context)

mypage = MypageView.as_view()
