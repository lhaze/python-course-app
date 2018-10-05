# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site

import factory


class SiteFactory(factory.DjangoModelFactory):

    class Meta:
        model = Site
        django_get_or_create = ('domain',)

    domain = factory.Sequence(lambda n: 'site_%d' % n)
    name = factory.LazyAttribute(lambda obj: obj.domain)
