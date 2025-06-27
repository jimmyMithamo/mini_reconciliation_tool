from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse    
from rest_framework import status  
# import csv and io for csv parsing
import csv
import io

class ApiView(APIView):
    def get(self, request):
        # return a list of the endpoints
        return Response({
            'api': reverse('api_view', request=request, format=None),
            'reconcile': reverse('reconciliation_view', request=request, format=None),
        })


# Helper function to parse CSV from an uploaded file
def parse_csv_file(uploaded_file):
    # Decode the file content from bytes to string
    file_data = uploaded_file.read().decode('utf-8')
    # Use io.StringIO to treat the string as a file for csv.DictReader
    csv_file = io.StringIO(file_data)
    reader = csv.DictReader(csv_file)
    data = []
    for row in reader:
        # Convert relevant fields to correct types (e.g., amount to float)
        processed_row = {
            (k.strip() if k else ''): (v.strip() if v else '') for k, v in row.items()
        }
        if 'amount' in processed_row and processed_row['amount']:
            try:
                processed_row['amount'] = float(processed_row['amount'])
            except ValueError:
                pass
        data.append(processed_row)
    return data


# ReconcileView for direct file upload
class ReconciliationView(APIView):
    def post(self, request, *args, **kwargs):
        # 1. Receive files from the frontend
        internal_uploaded_file = request.FILES.get('internal_file')
        provider_uploaded_file = request.FILES.get('provider_file')
        if internal_uploaded_file:
            print(internal_uploaded_file)
        if provider_uploaded_file:
            print(provider_uploaded_file)

        if not internal_uploaded_file or not provider_uploaded_file:
            return Response(
                {"error": "Both 'internal_file' and 'provider_file' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Parse CSV files on the backend
        try:
            internal_records = parse_csv_file(internal_uploaded_file)
            if internal_records:
                print(internal_records)
            provider_records = parse_csv_file(provider_uploaded_file)
            if provider_records:
                print(provider_records)
        except Exception as e:
            print(e)
            return Response(
                {"error": f"Error parsing CSV files: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not internal_records or not provider_records:
            return Response(
                {"error": "One or both CSV files are empty or malformed after parsing."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Perform Reconciliation Logic (largely the same as before)
        matched_transactions = []
        internal_only = []
        provider_only = []

        internal_lookup = {txn['transaction_reference']: txn for txn in internal_records if 'transaction_reference' in txn}

        for prov_txn in provider_records:
            ref = prov_txn.get('transaction_reference')
            if ref and ref in internal_lookup:
                internal_txn = internal_lookup[ref]

                combined_txn = {**internal_txn, **prov_txn}
                mismatch_details = {}

                internal_amount = internal_txn.get('amount')
                provider_amount = prov_txn.get('amount')
                if isinstance(internal_amount, (int, float)) and isinstance(provider_amount, (int, float)):
                    if abs(internal_amount - provider_amount) > 0.001:
                        mismatch_details['amount'] = f"Internal: {internal_amount}, Provider: {provider_amount}"
                else:
                    # Handle cases where amount might be string or missing after parsing
                    if str(internal_amount) != str(provider_amount):
                        mismatch_details['amount'] = f"Internal: {internal_amount}, Provider: {provider_amount} (Type mismatch or string comparison)"

                # check for status mismatch
                internal_status = internal_txn.get('status')
                provider_status = prov_txn.get('status')
                if internal_status and provider_status and internal_status.upper() != provider_status.upper():
                    mismatch_details['status'] = f"Internal: {internal_status}, Provider: {provider_status}"

                combined_txn['mismatchDetails'] = mismatch_details if mismatch_details else None
                matched_transactions.append(combined_txn)

                del internal_lookup[ref]
            else:
                # PRESENT ONLY IN PROVIDER FILE
                provider_only.append(prov_txn)

        # Any remaining transactions in internal_lookup are "Internal Only"
        internal_only = list(internal_lookup.values())

        # 4. Return Categorized Results
        return Response({
            "matchedTransactions": matched_transactions,
            "internalOnly": internal_only,
            "providerOnly": provider_only,
        }, status=status.HTTP_200_OK)

    # GET method for browsable API testing
    def get(self, request, *args, **kwargs):
        return Response({"message": "This is the reconciliation endpoint. Send a POST request with 'internal_file' and 'provider_file' (multipart/form-data)."},
                        status=status.HTTP_200_OK)
