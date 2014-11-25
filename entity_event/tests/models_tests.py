from datetime import datetime

from django.test import TestCase
from django_dynamic_fixture import N, G
from entity.models import Entity, EntityKind, EntityRelationship
from freezegun import freeze_time

from entity_event.models import (
    Medium, Source, SourceGroup, Unsubscription, Subscription, Event, EventActor, EventSeen
)


class SubscriptionSubscribedEntitiesTest(TestCase):
    def setUp(self):
        person_kind = G(EntityKind, name='person', display_name='person')
        superentity = G(Entity)
        sub1, sub2 = G(Entity, entity_kind=person_kind), G(Entity, entity_kind=person_kind)
        G(EntityRelationship, super_entity=superentity, sub_entity=sub1)
        G(EntityRelationship, super_entity=superentity, sub_entity=sub2)

        self.group_sub = N(Subscription, entity=superentity, sub_entity_kind=person_kind)
        self.indiv_sub = N(Subscription, entity=superentity, sub_entity_kind=None)

    def test_both_branches_return_queryset(self):
        group_qs = self.group_sub.subscribed_entities()
        indiv_qs = self.indiv_sub.subscribed_entities()
        self.assertEqual(type(group_qs), type(indiv_qs))

    def test_length_group(self):
        group_qs = self.group_sub.subscribed_entities()
        print self.group_sub.entity
        print group_qs
        self.assertEqual(group_qs.count(), 3)

    def test_length_indiv(self):
        indiv_qs = self.indiv_sub.subscribed_entities()
        self.assertEqual(indiv_qs.count(), 1)


# Note: The following freeze_time adds one second more than what we
# want to work around a strange off-by-one-second bug in
# freezegun. I'm not sure what other way to fix it.
@freeze_time(datetime(2014, 01, 01, 00, 00, 05))
class UnicodeTest(TestCase):
    def setUp(self):
        self.medium = N(Medium, display_name='Test Medium')
        self.source = N(Source, display_name='Test Source')
        self.source_group = N(SourceGroup, display_name='Test Source Group')
        self.entity = N(Entity, display_name='Test Entity')
        self.unsubscription = N(Unsubscription, entity=self.entity, medium=self.medium, source=self.source)
        self.subscription = N(Subscription, entity=self.entity, source=self.source, medium=self.medium)
        self.event = N(Event, source=self.source, context={}, id=1)
        self.event_actor = N(EventActor, event=self.event, entity=self.entity)
        self.event_seen = N(EventSeen, event=self.event, medium=self.medium, time_seen=datetime(2014, 01, 02))

    def test_medium_formats(self):
        s = unicode(self.medium)
        self.assertEqual(s, 'Test Medium')

    def test_source_formats(self):
        s = unicode(self.source)
        self.assertEqual(s, 'Test Source')

    def test_sourcegroup_formats(self):
        s = unicode(self.source_group)
        self.assertEqual(s, 'Test Source Group')

    def test_unsubscription_formats(self):
        s = unicode(self.unsubscription)
        self.assertEqual(s, 'Test Entity from Test Source by Test Medium')

    def test_subscription_formats(self):
        s = unicode(self.subscription)
        self.assertEqual(s, 'Test Entity to Test Source by Test Medium')

    def test_event_formats(self):
        s = unicode(self.event)
        print self.event.time
        print datetime.utcnow()
        self.assertTrue(s.startswith('Test Source event at 2014-01-01::00:00'))

    def test_eventactor_formats(self):
        s = unicode(self.event_actor)
        self.assertEqual(s, 'Event 1 - Test Entity')

    def test_event_seenformats(self):
        s = unicode(self.event_seen)
        self.assertEqual(s, 'Seen on Test Medium at 2014-01-02::00:00:00')