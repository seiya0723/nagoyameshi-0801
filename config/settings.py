"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-q0*^lcu^xy7x*$4=d8w*g9ognbybg20@hqg+#icd(rt1)=y4ml'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []


#################django-allauthでのメール認証設定ここから###################

#djangoallauthでメールでユーザー認証する際に必要になる認証バックエンド
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

#ログイン時の認証方法はemailとパスワードとする
ACCOUNT_AUTHENTICATION_METHOD   = "email"

#ログイン時にユーザー名(ユーザーID)は使用しない
ACCOUNT_USERNAME_REQUIRED       = False

#ユーザー登録時に入力したメールアドレスに、確認メールを送信する事を必須(mandatory)とする
ACCOUNT_EMAIL_VARIFICATION  = "mandatory"

#ユーザー登録画面でメールアドレス入力を要求する(True)
ACCOUNT_EMAIL_REQUIRED      = True


#DEBUGがTrueのとき、メールの内容は全て端末に表示させる(実際にメールを送信したい時はここをコメントアウトする)
if DEBUG:
    EMAIL_BACKEND   = "django.core.mail.backends.console.EmailBackend"
else:

    EMAIL_BACKEND   = "django.core.mail.backends.console.EmailBackend"

    """
    #TODO:SendgridのAPIキーと送信元メールアドレスを入れていない時、以下が実行されると必ずエラーになる点に注意。
    EMAIL_BACKEND       = "sendgrid_backend.SendgridBackend"
    DEFAULT_FROM_EMAIL  = "ここにデフォルトの送信元メールアドレスを指定"

    #【重要】APIキーの入力後、GitHubへのプッシュは厳禁。可能であれば.gitignoreに指定した別ファイルから読み込む
    SENDGRID_API_KEY    = "ここにsendgridのAPIkeyを記述する"

    #Sendgrid利用時はサンドボックスモードを無効化しておく。
    SENDGRID_SANDBOX_MODE_IN_DEBUG = False
    """

#################django-allauthでのメール認証設定ここまで###################




#django-allauth関係。django.contrib.sitesで使用するSITE_IDを指定する
SITE_ID = 1
#django-allauthログイン時とログアウト時のリダイレクトURL
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',


    'django.contrib.sites', # ←追加
    'allauth', # ←追加
    'allauth.account', # ←追加
    'allauth.socialaccount', # ←追加

    "nagoyameshi",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    "allauth.account.middleware.AccountMiddleware", # ←追加    
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / "templates",
                  BASE_DIR / "templates" / "allauth"
         ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# プロジェクト直下のstaticディレクトリを静的ファイルの保存場所とする。
if DEBUG:
    STATICFILES_DIRS = [ BASE_DIR / "static" ]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Stripeの設定

import os

# ここで環境変数を使う
# 環境変数: OSに設定されている変数のこと。OSに変数を書くことで、APIキーのような見せてはいけない情報を隠せる。
if "STRIPE_PUBLISHABLE_KEY" in os.environ and "STRIPE_API_KEY" in os.environ and "STRIPE_PRICE_ID" in os.environ:
    STRIPE_PUBLISHABLE_KEY  = os.environ["STRIPE_PUBLISHABLE_KEY"]
    STRIPE_API_KEY          = os.environ["STRIPE_API_KEY"]
    STRIPE_PRICE_ID         = os.environ["STRIPE_PRICE_ID"]


# Herokuデプロイの際に動かす設定。

if not DEBUG:

    #INSTALLED_APPSにcloudinaryの追加
    INSTALLED_APPS.append('cloudinary')
    INSTALLED_APPS.append('cloudinary_storage')

    # ALLOWED_HOSTSに(Djangoの公開を許可するホスト名(ドメイン名))を入力
    ALLOWED_HOSTS = [ os.environ["HOST"] ]

    # パスワードのハッシュ化、CSRFトークンの生成に使われる。
    SECRET_KEY = os.environ["SECRETKEY"]
    
    # 静的ファイル配信ミドルウェア、whitenoiseを使用。※ 順番不一致だと動かないため下記をそのままコピーする。
    MIDDLEWARE = [ 
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',

        "allauth.account.middleware.AccountMiddleware", # ←追加    
        ]

    # 静的ファイル(static)の存在場所を指定する。
    STATIC_ROOT = BASE_DIR / 'static'

    # DBの設定
    DATABASES = { 
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME'    : os.environ["DB_NAME"],
                'USER'    : os.environ["DB_USER"],
                'PASSWORD': os.environ["DB_PASSWORD"],
                'HOST'    : os.environ["DB_HOST"],
                'PORT': '5432',
                }
            }

    #DBのアクセス設定
    import dj_database_url

    db_from_env = dj_database_url.config(conn_max_age=600, ssl_require=True)
    DATABASES['default'].update(db_from_env)
    

    #cloudinaryの設定
    CLOUDINARY_STORAGE = { 
            'CLOUD_NAME': os.environ["CLOUD_NAME"], 
            'API_KEY'   : os.environ["API_KEY"], 
            'API_SECRET': os.environ["API_SECRET"],
            "SECURE"    : True,
            }

    #これは画像だけ(上限20MB)
    #DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

    #これは動画だけ(上限100MB)
    #DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.VideoMediaCloudinaryStorage'

    #これで全てのファイルがアップロード可能(上限20MB。ビュー側でアップロードファイル制限するなら基本これでいい)
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.RawMediaCloudinaryStorage'
