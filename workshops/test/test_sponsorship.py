from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from ..models import Event, Organization, Sponsorship
from .base import TestBase


class TestSponsorshipModel(TestBase):

    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(
            slug='2016-07-05-test-event',
            host=self.org_alpha,
        )

    def test_positive_amount_field(self):
        '''Check that we cannot add negative amount of sponsorship'''
        with self.assertRaises(ValidationError):
            Sponsorship.objects.create(
                organization=self.org_beta,
                event=self.event,
                amount=-500,
            ).full_clean()

    def test_sponsorship_without_amount(self):
        '''Check that we can have blank amount field'''
        Sponsorship.objects.create(
            organization=self.org_beta,
            event=self.event,
        ).full_clean()


    def test_sponsorship_can_be_deleted_and_related_objects_are_intact(self):
        '''Check that the event and organization aren't deleted'''
        sponsorship = Sponsorship.objects.create(
            organization=self.org_beta,
            event=self.event,
            amount=-500,
        )
        sponsorship.delete()
        with self.assertRaises(ObjectDoesNotExist):
            sponsorship.refresh_from_db()
        # Raise ObjectDoesNotExist if deleted
        self.event.refresh_from_db()
        self.org_beta.refresh_from_db()


class TestSponsorshipViews(TestBase):

    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(
            slug='2016-07-05-test-event',
            host=self.org_alpha,
        )
        self.sponsorship = Sponsorship.objects.create(
            organization=self.org_alpha,
            event=self.event,
        )
        self._setUpUsersAndLogin()

    def test_sponsor_visible_on_event_detail_page(self):
        '''Check that added sponsor is visible on the event detail page'''
        rv = self.client.get(
            reverse('event_details', kwargs={'slug': self.event.slug})
        )
        self.assertEqual(rv.status_code, 200)
        self.assertIn(self.sponsorship, rv.context['event'].sponsorship_set.all())

    def test_sponsor_visible_on_event_edit_page(self):
        rv = self.client.get(
            reverse('event_edit', kwargs={'slug': self.event.slug})
        )
        self.assertEqual(rv.status_code, 200)
        self.assertIn(self.sponsorship, rv.context['object'].sponsorship_set.all())

    def test_add_sponsor_with_amount(self):
        '''Check that we can add a sponsor from `event_edit` view'''
        payload = {
            'sponsor-organization': self.org_beta.pk,
            'sponsor-event': self.event.pk,
            'sponsor-amount': 100.00,
        }
        response = self.client.post(
            reverse('event_edit', kwargs={'slug': self.event.slug}),
            payload,
            follow=True
        )
        self.assertRedirects(
            response,
            '{}#sponsors'.format(
                reverse('event_edit', kwargs={'slug': self.event.slug}),
            )
        )
        self.assertTrue(response.context['object'].sponsorship_set.all())
        self.assertEqual(response.context['object'].sponsors.count(), 2)

    def test_add_sponsor_without_amount(self):
        '''Check that we can add a sponsor w/o amount from `event_edit` view'''
        payload = {
            'sponsor-organization': self.org_beta.pk,
            'sponsor-event': self.event.pk,
        }
        response = self.client.post(
            reverse('event_edit', kwargs={'slug': self.event.slug}),
            payload,
            follow=True
        )
        self.assertRedirects(
            response,
            '{}#sponsors'.format(
                reverse('event_edit', kwargs={'slug': self.event.slug}),
            )
        )
        self.assertTrue(response.context['object'].sponsorship_set.all())
        self.assertEqual(response.context['object'].sponsors.count(), 2)

    def test_delete_sponsor(self):
        '''Check that we can delete a sponsor from `sponsor_delete` view'''
        response = self.client.post(
            reverse('sponsorship_delete', kwargs={'pk': self.sponsorship.pk}),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('event_edit', kwargs={'slug': self.event.slug})
        )
        self.assertFalse(response.context['object'].sponsorship_set.all())
        self.assertEqual(response.context['object'].sponsors.count(), 0)
        with self.assertRaises(ObjectDoesNotExist):
            self.sponsorship.refresh_from_db()
