from django.conf import settings
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views



urlpatterns = [
    url(r'^$', views.homepage, name="homepage"),
    url(r'^signup/$', views.signup, name="signup"),
    #login 템플릿이름 세팅해준 이유는 기본적으로 html이름이 장고내에 디폴트값으로 있는데
    #regration/login.html인가 그렇습니다.() 정확히는 기억이안납니다.)
    #어쨋든 kwargs인자를 통해서 지정을 해줍니다.
    url(r'^login/$', auth_views.login, name="login",
        kwargs={"template_name":"accounts/login_form.html"}),

    #logout시에 next_page를 세팅해줌으로써 어디로 갈지 지정해주는 것 
    #settings.LOGIN_URL이라고 적은건데 로그아웃하면 로그인페이지로 넘겨준다.
    #하지만 프로젝트폴더(현재 deepmining이름)에 templates/layout.html을 보시면 
    #<li><a href="{% url 'logout' %}?next={{ request.path }}">로그아웃</a></li> 이런 문구가 나옵니다.
    #?next= 이걸 지정해주면 여기서 처리한 대로 로그아웃시에 페이지를 넘겨줍니다.
    #?next= 지정해주지 않으면 url에 세팅되어있는 kwargs={"next_page":settings.LOGIN_URL} 로그인페이지로 넘어갑니다.
    #?next=인자는 보통 로그인/로그아웃시에는 ?next={{ request.path }} 이렇게 지정해주는게 좋습니다. (프로젝트폴더/templates/layout.html확인요망)
    # ?next={{ request.path }}의 해석은 로그인/로그아웃 시에 현재 보고있는 페이지로 다시 돌아온다는 뜻으로 해석을 하시면 됩니다.
    #이유는 쇼핑몰을 예로들면 상품보고있다가 로그인하면 그 화면으로 다시 돌아와야하는데 이걸지정해주지 않으면 장고 로그인시 디폴트값으로 
    #url이 로그인시 지정되어있는 주소로 이동을 하게됩니다.
    url(r'^logout/$', auth_views.logout, name="logout",
        kwargs={"next_page":settings.LOGIN_URL}),
    url(r'^profile/$', views.profile, name="profile"),
]
