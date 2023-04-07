from server import hooks

from .api.v1.viewsets import PartnerEntryViewSet


@hooks.register("API_V1_PARTNER_VIEWSET")
def register_partner_ticket_viewsets():
    return {
        "prefix": "entry",
        "viewset": PartnerEntryViewSet,
        "basename": "partnerentry",
    }
