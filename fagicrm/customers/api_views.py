# fagicrm/customers/api_views.py
# Updated customers API to support Select2 AJAX lookups, OPTIONS preflight, DEBUG-friendly CORS,
# and safe API-key handling. Returns Select2-compatible JSON: { results: [{id, text, ...}], pagination: { more: bool } }

from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
import logging

from .models import Customer, Lead
from employees.models import Employee

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def health_check(request):
    """Health check endpoint for integration testing"""
    # Handle preflight
    if request.method == "OPTIONS":
        resp = HttpResponse()
        if settings.DEBUG:
            resp["Access-Control-Allow-Origin"] = "*"
            resp["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            resp["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        return resp

    return JsonResponse({
        'status': 'ok',
        'service': 'FagiCRM',
        'version': '1.0.0',
        'timestamp': timezone.now().isoformat()
    })


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def customers_api(request):
    """
    Customers API used for AJAX Select2 lookups and integration.

    Query parameters:
      - search: search term (applies to first_name, last_name, company_name, email, phone)
      - page: page number (Select2 paging starts at 1)
      - page_size: items per page (default 20)
      - status: optional status filter
      - simple: if '1' returns the simple Select2 fields only (id/text)

    Authentication:
      - Header 'Authorization: Bearer <API_KEY>' expected in production.
      - When settings.DEBUG is True, anonymous access is allowed for developer convenience.

    Response (Select2 format):
      {
        "results": [{ "id": <id>, "text": "<display text>", ...optional fields... }],
        "pagination": { "more": true|false }
      }
    """
    # Preflight / CORS handling
    if request.method == "OPTIONS":
        resp = HttpResponse()
        if settings.DEBUG:
            resp["Access-Control-Allow-Origin"] = "*"
            resp["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            resp["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        return resp

    # API key (simple scheme)
    api_key = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    if not api_key and not settings.DEBUG:
        return JsonResponse({'error': 'API key required'}, status=401)

    try:
        qs = Customer.objects.all().select_related('assigned_employee__user')

        # Search
        search = (request.GET.get('search') or '').strip()
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(company_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )

        # Filter by status (optional)
        status_filter = request.GET.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        # Pagination params
        try:
            page_size = int(request.GET.get('page_size', 20))
        except (ValueError, TypeError):
            page_size = 20

        try:
            page = int(request.GET.get('page', 1))
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1

        # Ordering
        qs = qs.order_by('first_name', 'last_name')

        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page)
        customers = page_obj.object_list

        results = []
        simple = request.GET.get('simple') == '1'

        for c in customers:
            # Build display text used by Select2
            name_parts = []
            if getattr(c, 'first_name', None):
                name_parts.append(c.first_name)
            if getattr(c, 'last_name', None):
                name_parts.append(c.last_name)
            name = " ".join(name_parts).strip()
            if not name and getattr(c, 'company_name', None):
                name = c.company_name or ""
            contact = c.phone or c.email or ""
            display = f"{name} - {contact}" if contact else name or f"Customer {c.id}"

            if simple:
                results.append({'id': c.id, 'text': display})
            else:
                # include extra helpful fields for the frontend
                assigned = None
                if getattr(c, 'assigned_employee', None):
                    ae = c.assigned_employee
                    assigned = {
                        'id': ae.id,
                        'employee_id': getattr(ae, 'employee_id', None),
                        'position': getattr(ae, 'position', None),
                        'department': getattr(ae.department, 'name', None) if getattr(ae, 'department', None) else None,
                        'user': {
                            'id': ae.user.id,
                            'username': ae.user.username,
                            'first_name': ae.user.first_name,
                            'last_name': ae.user.last_name,
                            'email': ae.user.email,
                        } if getattr(ae, 'user', None) else None
                    }

                results.append({
                    'id': c.id,
                    'text': display,
                    'first_name': c.first_name,
                    'last_name': c.last_name,
                    'company_name': c.company_name,
                    'email': c.email,
                    'phone': c.phone,
                    'address_line1': c.address_line1,
                    'address_line2': c.address_line2,
                    'city': c.city,
                    'state': c.state,
                    'postal_code': c.postal_code,
                    'country': c.country,
                    'status': c.status,
                    'customer_type': c.customer_type,
                    'created_at': c.created_at.isoformat() if getattr(c, 'created_at', None) else None,
                    'updated_at': c.updated_at.isoformat() if getattr(c, 'updated_at', None) else None,
                    'assigned_employee': assigned
                })

        more = page_obj.has_next()

        response = JsonResponse({
            'results': results,
            'pagination': {'more': more},
            'count': paginator.count,
            'page': page_obj.number,
            'num_pages': paginator.num_pages
        })

        # Allow development CORS (so assetmanager on different port can query)
        if settings.DEBUG:
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"

        return response

    except Exception as exc:
        logger.exception("customers_api error")
        return JsonResponse({'error': str(exc)}, status=500)
        
@csrf_exempt
@require_http_methods(["GET"])
def employees_api(request):
    """API endpoint to get employees for asset manager integration"""
    # Simple API key authentication
    api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not api_key:
        return JsonResponse({'error': 'API key required'}, status=401)
    
    try:
        employees = Employee.objects.filter(employment_status='active').select_related('user', 'department')
        
        # Serialize employee data
        employees_data = []
        for employee in employees:
            employee_data = {
                'id': employee.id,
                'employee_id': employee.employee_id,
                'user': {
                    'id': employee.user.id,
                    'username': employee.user.username,
                    'first_name': employee.user.first_name,
                    'last_name': employee.user.last_name,
                    'email': employee.user.email,
                },
                'phone': employee.phone,
                'position': employee.position,
                'employment_status': employee.employment_status,
                'employment_type': employee.employment_type,
                'hire_date': employee.hire_date.isoformat(),
                'department': {
                    'id': employee.department.id,
                    'name': employee.department.name,
                    'description': employee.department.description,
                } if employee.department else None,
                'manager': {
                    'id': employee.manager.id,
                    'employee_id': employee.manager.employee_id,
                    'name': employee.manager.full_name,
                } if employee.manager else None,
            }
            employees_data.append(employee_data)
        
        return JsonResponse({
            'results': employees_data,
            'count': len(employees_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def asset_assignments_api(request):
    """API endpoint to receive asset assignment data from asset manager"""
    # Simple API key authentication
    api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not api_key:
        return JsonResponse({'error': 'API key required'}, status=401)
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['customer_id', 'asset_tag', 'asset_name']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
        
        # Find the customer
        try:
            customer = Customer.objects.get(id=data['customer_id'])
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer not found'}, status=404)
        
        # For now, we'll just log the assignment data
        # In a full implementation, you might want to store this in a separate model
        # or add notes to the customer record
        
        # Add a note to the customer about the asset assignment
        from .models import CustomerNote
        from django.contrib.auth.models import User
        
        # Try to find a system user for the note
        system_user = User.objects.filter(is_staff=True).first()
        if not system_user:
            system_user = User.objects.first()
        
        note_content = f"Asset Assignment: {data['asset_tag']} - {data['asset_name']}\n"
        note_content += f"Assignment Type: {data.get('assignment_type', 'Unknown')}\n"
        note_content += f"Assigned Date: {data.get('assigned_date', 'Unknown')}\n"
        
        if data.get('contract_number'):
            note_content += f"Contract: {data['contract_number']}\n"
        
        if data.get('monthly_fee'):
            note_content += f"Monthly Fee: ${data['monthly_fee']}\n"
        
        if data.get('total_value'):
            note_content += f"Total Value: ${data['total_value']}\n"
        
        if data.get('notes'):
            note_content += f"Notes: {data['notes']}\n"
        
        CustomerNote.objects.create(
            customer=customer,
            note=note_content,
            created_by=system_user,
            is_important=True
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Asset assignment recorded',
            'customer_id': customer.id,
            'asset_tag': data['asset_tag']
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def customer_detail_api(request, customer_id):
    """API endpoint to get detailed customer information"""
    # Simple API key authentication
    api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not api_key:
        return JsonResponse({'error': 'API key required'}, status=401)
    
    try:
        customer = Customer.objects.select_related('assigned_employee__user').get(id=customer_id)
        
        customer_data = {
            'id': customer.id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'company_name': customer.company_name,
            'email': customer.email,
            'phone': customer.phone,
            'alternate_phone': customer.alternate_phone,
            'address_line1': customer.address_line1,
            'address_line2': customer.address_line2,
            'city': customer.city,
            'state': customer.state,
            'postal_code': customer.postal_code,
            'country': customer.country,
            'status': customer.status,
            'customer_type': customer.customer_type,
            'preferred_contact_method': customer.preferred_contact_method,
            'total_spent': float(customer.total_spent),
            'lifetime_value': float(customer.lifetime_value),
            'created_at': customer.created_at.isoformat(),
            'updated_at': customer.updated_at.isoformat(),
            'assigned_employee': None
        }
        
        # Include assigned employee data
        if customer.assigned_employee:
            customer_data['assigned_employee'] = {
                'id': customer.assigned_employee.id,
                'employee_id': customer.assigned_employee.employee_id,
                'user': {
                    'id': customer.assigned_employee.user.id,
                    'username': customer.assigned_employee.user.username,
                    'first_name': customer.assigned_employee.user.first_name,
                    'last_name': customer.assigned_employee.user.last_name,
                    'email': customer.assigned_employee.user.email,
                },
                'position': customer.assigned_employee.position,
                'department': customer.assigned_employee.department.name if customer.assigned_employee.department else None,
            }
        
        # Include recent notes
        recent_notes = customer.notes.all()[:5]
        customer_data['recent_notes'] = []
        for note in recent_notes:
            customer_data['recent_notes'].append({
                'id': note.id,
                'note': note.note,
                'is_important': note.is_important,
                'created_at': note.created_at.isoformat(),
                'created_by': note.created_by.get_full_name() if note.created_by else 'System'
            })
        
        return JsonResponse(customer_data)
        
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Customer not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
