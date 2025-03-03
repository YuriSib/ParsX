from service.forms import OrderForm


def get_context_data(request):
    context = {
        'create_order': OrderForm #Назвать нужно в соответствии с url
    }
    return context