from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import View

from tg.bot import Bot
from tg.models import Chat


@login_required
def me(request):
    coder = request.user.coder
    url = 'https://telegram.me/ClistBot?start'

    chat = coder.chat
    if chat is None:
        chat = Chat.objects.create(coder=coder)
    if not chat.chat_id:
        chat.secret_key = User.objects.make_random_password(length=20)
        url += '=' + chat.secret_key
        chat.save()

    return HttpResponseRedirect(url)


@login_required
def unlink(request):
    coder = request.user.coder
    coder.chat.delete()
    return HttpResponseRedirect(reverse('coder:settings', kwargs=dict(tab='social')))


class Incoming(View):

    def post(self, request):
        bot = Bot()
        try:
            bot.incoming(request.body)
        except Exception as e:
            bot.logger.critical(e)
        return HttpResponse('ok')
