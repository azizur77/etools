
import datetime
import json

from unicef_vision.loaders import VISION_NO_DATA_MESSAGE

from etools.applications.EquiTrack.tests.cases import BaseTenantTestCase
from etools.applications.partners import synchronizers
from etools.applications.partners.models import PartnerOrganization
from etools.applications.partners.tests.factories import PartnerFactory
from etools.applications.users.models import Country


class TestPartnerSynchronizer(BaseTenantTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.first()

    def setUp(self):
        self.data = {
            "PARTNER_TYPE_DESC": "UN AGENCY",
            "VENDOR_NAME": "ACME Inc.",
            "VENDOR_CODE": "ACM",
            "COUNTRY": "USD",
            "TOTAL_CASH_TRANSFERRED_CP": "150.00",
            "TOTAL_CASH_TRANSFERRED_CY": "100.00",
            "NET_CASH_TRANSFERRED_CY": "90.00",
            "REPORTED_CY": "80.00",
            "TOTAL_CASH_TRANSFERRED_YTD": "70.00",
        }
        self.records = {"ROWSET": {"ROW": [self.data]}}
        self.adapter = synchronizers.PartnerSynchronizer(self.country.business_area_code)

    def test_convert_records(self):
        self.assertEqual(
            self.adapter._convert_records(json.dumps(self.records)),
            [self.data]
        )

    def test_filter_records(self):
        """Ensure records maintained"""
        response = self.adapter._filter_records([self.data])
        self.assertEqual(response, [self.data])

    def test_filter_records_no_vendor_name(self):
        """If missing vendor name ignore record"""
        self.data["VENDOR_NAME"] = ""
        response = self.adapter._filter_records([self.data])
        self.assertEqual(response, [])

    def test_get_json(self):
        response = self.adapter._get_json(self.data)
        self.assertEqual(response, self.data)

    def test_get_json_no_data(self):
        response = self.adapter._get_json(VISION_NO_DATA_MESSAGE)
        self.assertEqual(response, [])

    def test_get_cso_type_none(self):
        self.assertIsNone(self.adapter.get_cso_type(self.data))

    def test_get_cso_type(self):
        self.data["CSO_TYPE"] = "National NGO"
        self.assertEqual(self.adapter.get_cso_type(self.data), "National")

    def test_get_partner_type_none(self):
        self.data["PARTNER_TYPE_DESC"] = "Wrong"
        self.assertIsNone(self.adapter.get_partner_type(self.data))

    def test_get_partner_type(self):
        self.assertEqual(self.adapter.get_partner_type(self.data), "UN Agency")

    def test_get_partner_rating_none(self):
        self.assertEqual('', self.adapter.get_partner_rating(self.data))

    def test_get_partner_rating(self):
        self.data["RISK_RATING"] = "High"
        self.assertEqual(self.adapter.get_partner_rating(self.data), "High")

    def test_save_records_no_type(self):
        """Check that partner organization record is created,
        no type mapping
        """
        self.data["PARTNER_TYPE_DESC"] = "Supplier"
        self.data["VENDOR_CODE"] = "123"
        partner_qs = PartnerOrganization.objects.filter(
            vendor_number=self.data["VENDOR_CODE"]
        )
        self.assertFalse(partner_qs.exists())
        response = self.adapter._save_records([self.data])
        self.assertEqual(response, 0)
        self.assertTrue(partner_qs.exists())
        partner = partner_qs.first()
        self.assertEqual(partner.name, "")

    def test_save_records(self):
        """Check that partner organization record is created,
        type mapping matches
        """
        self.data["VENDOR_CODE"] = "124"
        partner_qs = PartnerOrganization.objects.filter(
            vendor_number=self.data["VENDOR_CODE"]
        )
        self.assertFalse(partner_qs.exists())
        num_saved = self.adapter._save_records([self.data])
        self.assertEqual(num_saved, 1)
        self.assertTrue(partner_qs.exists())
        partner = partner_qs.first()
        self.assertEqual(partner.name, self.data["VENDOR_NAME"])

    def test_save_records_update_name(self):
        """Check that partner organization record is updated,
        name changed
        """
        partner = PartnerFactory(
            name="New",
            vendor_number=self.data["VENDOR_CODE"]
        )
        response = self.adapter._save_records([self.data])
        self.assertEqual(response, 1)
        partner_updated = PartnerOrganization.objects.get(pk=partner.pk)
        self.assertEqual(partner_updated.name, self.data["VENDOR_NAME"])

    def test_save_records_update_deleted_flag(self):
        """Check that partner organization record is updated,
        deleted_flag changed
        """
        self.data["MARKED_FOR_DELETION"] = 'X'
        partner = PartnerFactory(
            name=self.data["VENDOR_NAME"],
            vendor_number=self.data["VENDOR_CODE"],
            deleted_flag=False
        )
        response = self.adapter._save_records([self.data])
        self.assertEqual(response, 1)
        partner_updated = PartnerOrganization.objects.get(pk=partner.pk)
        self.assertTrue(partner_updated.deleted_flag)

    def test_save_records_update_date(self):
        """Check that partner organization record is updated,
        last assessment date changed
        """
        self.data["DATE_OF_ASSESSMENT"] = "4-Apr-17"
        partner = PartnerFactory(
            name=self.data["VENDOR_NAME"],
            vendor_number=self.data["VENDOR_CODE"],
            country=self.data["COUNTRY"],
            last_assessment_date=datetime.date(2017, 4, 5),
        )
        response = self.adapter._save_records([self.data])
        self.assertEqual(response, 1)
        partner_updated = PartnerOrganization.objects.get(pk=partner.pk)
        self.assertEqual(
            partner_updated.last_assessment_date,
            datetime.date(2017, 4, 4)
        )

    def test_save_records_update(self):
        """Check that partner organization record is NOT updated,
        if no change
        """
        PartnerFactory(
            name=self.data["VENDOR_NAME"],
            vendor_number=self.data["VENDOR_CODE"],
            country=self.data["COUNTRY"],
            partner_type="UN Agency",
            total_ct_cp=self.data["TOTAL_CASH_TRANSFERRED_CP"],
            total_ct_cy=self.data["TOTAL_CASH_TRANSFERRED_CY"],
        )
        response = self.adapter._save_records([self.data])
        self.assertEqual(response, 1)


class TestDCTSynchronizer(BaseTenantTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.first()
        cls.vendor_key = '007'
        cls.api_response = [
            {
                'VENDOR_NAME': None,
                'VENDOR_CODE': cls.vendor_key,
                'WBS_ELEMENT_EX': None,
                'GRANT_REF': None,
                'DONOR_NAME': None,
                'EXPIRY_DATE': '2012-12-31T00:00:00-05:00',
                'COMMITMENT_REF': None,
                'DCT_AMT_USD': '0',
                'LIQUIDATION_AMT_USD': '0',
                'OUTSTANDING_BALANCE_USD': '0',
                'AMT_LESS3_MONTHS_USD': '0',
                'AMT_3TO6_MONTHS_USD': 30,
                'AMT_6TO9_MONTHS_USD': 60,
                'AMT_MORE9_MONTHS_USD': 90,
            },
            {
                'VENDOR_NAME': None,
                'VENDOR_CODE': cls.vendor_key,
                'WBS_ELEMENT_EX': None,
                'GRANT_REF': None,
                'DONOR_NAME': None,
                'EXPIRY_DATE': '2012-12-31T00:00:00-05:00',
                'COMMITMENT_REF': None,
                'DCT_AMT_USD': '0',
                'LIQUIDATION_AMT_USD': '0',
                'OUTSTANDING_BALANCE_USD': '0',
                'AMT_LESS3_MONTHS_USD': '0',
                'AMT_3TO6_MONTHS_USD': 300,
                'AMT_6TO9_MONTHS_USD': 600,
                'AMT_MORE9_MONTHS_USD': 900,
            },
            {
                'VENDOR_NAME': None,
                'VENDOR_CODE': '123',
                'WBS_ELEMENT_EX': None,
                'GRANT_REF': None,
                'DONOR_NAME': None,
                'EXPIRY_DATE': '2012-12-31T00:00:00-05:00',
                'COMMITMENT_REF': '0',
                'DCT_AMT_USD': '0',
                'LIQUIDATION_AMT_USD': '0',
                'OUTSTANDING_BALANCE_USD': '0',
                'AMT_LESS3_MONTHS_USD': '0',
                'AMT_3TO6_MONTHS_USD': 3000,
                'AMT_6TO9_MONTHS_USD': 6000,
                'AMT_MORE9_MONTHS_USD': 9000,
            }
        ]

        cls.partner = PartnerFactory(
            name="New",
            vendor_number=cls.vendor_key
        )
        cls.synchronizer = synchronizers.DirectCashTransferSynchronizer(cls.country.business_area_code)

    def test_create_dict(self):
        dcts = self.synchronizer.create_dict(self.api_response)
        self.assertEqual(len(dcts.keys()), 2)
        self.assertEqual(dcts[self.vendor_key]['outstanding_dct_amount_6_to_9_months_usd'], 660)
        self.assertEqual(dcts[self.vendor_key]['outstanding_dct_amount_more_than_9_months_usd'], 990)

    def test_save(self):
        self.assertEqual(self.partner.outstanding_dct_amount_6_to_9_months_usd, None)
        self.assertEqual(self.partner.outstanding_dct_amount_more_than_9_months_usd, None)
        partner_to_update = {
            self.vendor_key: {
                'outstanding_dct_amount_6_to_9_months_usd': 100,
                'outstanding_dct_amount_more_than_9_months_usd': 200},
        }
        self.synchronizer._save(partner_to_update)
        partner = PartnerOrganization.objects.get(vendor_number=self.vendor_key)
        self.assertEqual(partner.outstanding_dct_amount_6_to_9_months_usd, 100)
        self.assertEqual(partner.outstanding_dct_amount_more_than_9_months_usd, 200)

    def test_save_records(self):
        self.synchronizer._save_records(self.api_response)
        partner = PartnerOrganization.objects.get(vendor_number=self.vendor_key)
        self.assertEqual(partner.outstanding_dct_amount_6_to_9_months_usd, 660)
        self.assertEqual(partner.outstanding_dct_amount_more_than_9_months_usd, 990)
