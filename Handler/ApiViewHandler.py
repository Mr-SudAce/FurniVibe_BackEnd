from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from django.http import Http404

# -------------------------------
# CREATE
# -------------------------------


def handle_create(
    serializer_class,
    request,
    success_message="Created successfully",
    error_message="Creation failed",
):
    # Pass context to serializer (useful for request.user access if needed)
    serializer = serializer_class(data=request.data, context={'request': request})

    if not serializer.is_valid():
        return Response(
            {
                "status": False,
                "message": serializer.errors,
                "error": error_message,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        with transaction.atomic():
            serializer.save()
    except IntegrityError as e:
        return Response(
            {
                "status": False,
                "message": "Database constraint error",
                "detail": str(e),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "status": True,
            "message": success_message,
            "data": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


# -------------------------------
# GET ALL
# -------------------------------
def handle_getAll(*, model, serializer_class, not_found_message):
    try:
        objects = model.objects.all()
        serialized = serializer_class(objects, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"message": not_found_message, "error": str(e)},
            status=status.HTTP_404_NOT_FOUND,
        )


# -------------------------------
# GET BY ID
# -------------------------------
def handle_get_byid(
    model, serializer_class, obj_id, not_found_message="Object not found"
):
    try:
        obj = get_object_or_404(model, id=obj_id)
        serializer = serializer_class(obj)
    except Http404:
        return Response(
            {"message": not_found_message},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response(serializer.data, status=status.HTTP_200_OK)


# -------------------------------
# UPDATE
# -------------------------------
def handle_update(
    model,
    serializer_class,
    obj_id,
    request,
    success_message="Updated successfully",
    error_message="Update failed",
):
    obj = get_object_or_404(model, id=obj_id)
    serializer = serializer_class(obj, data=request.data, partial=True, context={'request': request})

    if serializer.is_valid():
        try:
            with transaction.atomic():
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": success_message,
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
        except IntegrityError:
            return Response(
                {"status": False, "message": "Update caused duplicate data"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response(
        {"status": False, "message": serializer.errors, "errors": error_message},
        status=status.HTTP_400_BAD_REQUEST,
    )


# -------------------------------
# DELETE
# -------------------------------
def handle_deletion(
    model,
    obj_id,
    success_message="Deleted successfully",
    error_message="Deletion failed",
):
    obj = get_object_or_404(model, id=obj_id)

    try:
        with transaction.atomic():
            obj.delete()
            return Response(
                {"status": True, "message": success_message},
                status=status.HTTP_204_NO_CONTENT,
            )
    except Exception as e:
        return Response(
            {"status": False, "error": error_message, "detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
