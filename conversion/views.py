from django.http import JsonResponse, HttpResponse
from decimal import Decimal, InvalidOperation
from .models import CurrencyPair


def currency_conversion(request, currency1, currency2, amount):
    """
    Endpoint for currency conversion.

    Args:
        currency1: Source currency code (e.g., USD)
        currency2: Target currency code (e.g., EUR)
        amount: Amount to convert

    Returns:
        JSON response with conversion details or appropriate error status
    """
    if request.method != 'GET':
        return HttpResponse(status=405)

    try:
        try:
            currency_pair = CurrencyPair.objects.get(
                source_currency=currency1,
                destination_currency=currency2
            )

            amount_decimal = Decimal(amount)

            converted_amount = amount_decimal * currency_pair.conversion_rate

            return JsonResponse({
                'from_currency': currency1,
                'to_currency': currency2,
                'amount': str(amount_decimal),
                'converted_amount': str(converted_amount.quantize(Decimal('0.01'))),
                'conversion_rate': str(currency_pair.conversion_rate)
            })

        except CurrencyPair.DoesNotExist:
            return JsonResponse({"error": f"No direct conversion available for {currency1} to {currency2}"}, status=400)


    except (ValueError, InvalidOperation):
        return JsonResponse({"error": f"Invalid amount format: {amount}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

