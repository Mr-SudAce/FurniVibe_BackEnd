from .models import OtherDetailModel


def dashboard_context(request):
    """Makes company details from OtherDetailModel available to all templates."""
    other_details = OtherDetailModel.objects.first()
    return {"other_details": other_details}