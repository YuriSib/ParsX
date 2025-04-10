from django.urls import path
# from views import SitemapXmlView
from django.views.generic import TemplateView


app_name = 'core'

urlpatterns = [
    path("", TemplateView.as_view(
        template_name="service/main.html",
        content_type="text/html"
    )),
    path("yandex_68541018caec36ca.html",
         TemplateView.as_view(
             template_name="seo/yandex_68541018caec36ca.html",
             content_type="text/html"
    )),
    path("google847e52bf59cb1536.html",
         TemplateView.as_view(
             template_name="seo/google847e52bf59cb1536.html",
             content_type="text/html"
    )),
    path("robots.txt", TemplateView.as_view(
        template_name="seo/robots.txt",
        content_type="text/plain"
    )),
    path('sitemap.xml', TemplateView.as_view(
        template_name="seo/sitemapxml.html",
        content_type="text/html"
    )),
   ]
