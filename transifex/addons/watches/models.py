# -*- coding: utf-8 -*-
import traceback
from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from happix.models import Resource
from languages.models import Language
from txcommon.db.models import IntegerTupleField
from txcommon.log import logger

from projects.models import Project
#Project = get_model('projects', 'Project')

from notification.models import ObservedItem, is_observing

class WatchException(StandardError):
    pass

class TranslationWatch(models.Model):
    """
    An unique association of a Resource and a Language to be watched.

    Different translators eventually will use the same TranslationWatch
    objects for watching translation changes.
    """
    resource = models.ForeignKey(Resource,
        help_text=_('Resource to watch.'))
    language = models.ForeignKey(Language,
        help_text=_('Language of the translation.'))

    def __unicode__(self):
        return u'%s (%s)' % (self.resource.full_name, self.language)

    def __repr__(self):
        return u'<TranslationWatch: %s (%s)>' % (
            self.resource.full_name, self.language)

    class Meta:
        unique_together = ('resource', 'language')
        verbose_name = _('translation watch')
        verbose_name_plural = _('translation watches')


def is_watched(self, user, signal=None):
    """
    Return a boolean value if an object is watched by an user or not

    It is possible also verify if it is watched by a user in a specific 
    signal, passing the signal as a second parameter
    """
    if signal:
        return is_observing(self, user, signal)

    if isinstance(user, AnonymousUser):
        return False

    ctype = ContentType.objects.get_for_model(self)
    observed_items = ObservedItem.objects.filter(content_type=ctype,
        object_id=self.id, user=user)
    if observed_items:
        return True
    else:
        return False


Project.add_to_class("is_watched", is_watched)
TranslationWatch.add_to_class("is_watched", is_watched)