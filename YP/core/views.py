# from django.views.generic import TemplateView, ListView
# from django.urls import reverse_lazy
#
# from ..service.models import Service


# class SitemapXmlView(TemplateView):
#     template_name = 'seo/sitemapxml.html'
#     content_type = 'application/xml'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['service'] = Service.objects.filter(active=True)
#         return context
