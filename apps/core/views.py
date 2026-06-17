import json
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect
from apps.freight.models import FreightOrder
from apps.payments.models import Payment
from apps.drivers.models import DriverProfile
from apps.vehicles.models import Vehicle
from apps.cargo.models import CargoType
from apps.tracking.models import TrackingEvent

# =====================================================================
# API ENDPOINTS — RELATÓRIOS E METRICAS OPERACIONAIS
# =====================================================================

class AdminDashboardAPIView(APIView):
    """
    GET /api/admin/dashboard/
    Endpoint consolidating essential operational KPIs for the master dashboard.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.user.user_type not in ['ADMIN', 'SUPPORT', 'FINANCE', 'LOGISTICS']:
            return Response({"success": False, "message": "Acesso negado."}, status=status.HTTP_403_FORBIDDEN)

        total_orders = FreightOrder.objects.count()
        ongoing_orders = FreightOrder.objects.filter(
            status__in=[
                'waiting_driver', 'driver_found', 'driver_going_to_pickup', 
                'arrived_at_origin', 'cargo_collected', 'in_transit', 
                'temporarily_stopped', 'route_deviation_detected', 'near_destination', 'arrived_at_destination'
            ]
        ).count()
        completed_orders = FreightOrder.objects.filter(status='completed').count()
        cancelled_orders = FreightOrder.objects.filter(status='cancelled').count()

        # Financial summaries
        revenue_sum = Payment.objects.filter(status='paid').aggregate(models.Sum('amount'))['amount__sum'] or Decimal("0.00")
        pending_sum = Payment.objects.filter(status='pending').aggregate(models.Sum('amount'))['amount__sum'] or Decimal("0.00")
        
        # Operational resources
        online_drivers = DriverProfile.objects.filter(is_online=True).count()
        available_vehicles = Vehicle.objects.filter(status='approved').count()
        avg_rating = DriverProfile.objects.filter(status='approved').aggregate(models.Avg('rating'))['rating__avg'] or 5.00

        data = {
            "kpis": {
                "total_orders": total_orders,
                "ongoing_orders": ongoing_orders,
                "completed_orders": completed_orders,
                "cancelled_orders": cancelled_orders,
                "total_revenue": str(Decimal(revenue_sum).quantize(Decimal("0.01"))),
                "pending_payments": str(Decimal(pending_sum).quantize(Decimal("0.01"))),
                "online_drivers": online_drivers,
                "available_vehicles": available_vehicles,
                "average_driver_rating": round(float(avg_rating), 2)
            }
        }

        return Response({
            "success": True,
            "data": data,
            "message": "Indicadores gerais obtidos com sucesso."
        }, status=status.HTTP_200_OK)

class OperationsReportAPIView(APIView):
    """
    GET /api/admin/reports/operations/
    Generates statistics on freight volumes, status categories, and vehicle types.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.user.user_type not in ['ADMIN', 'SUPPORT', 'LOGISTICS']:
            return Response({"success": False, "message": "Acesso negado."}, status=status.HTTP_403_FORBIDDEN)

        # Orders by status breakdown
        status_counts = FreightOrder.objects.values('status').annotate(count=models.Count('id'))
        
        # Orders by cargo category
        cargo_counts = FreightOrder.objects.values('cargo_category').annotate(count=models.Count('id'))

        # Vehicles by status breakdown
        vehicle_counts = Vehicle.objects.values('vehicle_type').annotate(count=models.Count('id'))

        data = {
            "status_distribution": {item['status']: item['count'] for item in status_counts},
            "cargo_distribution": {item['cargo_category']: item['count'] for item in cargo_counts},
            "vehicle_type_distribution": {item['vehicle_type']: item['count'] for item in vehicle_counts}
        }

        return Response({
            "success": True,
            "data": data,
            "message": "Relatório operacional consolidado com sucesso."
        }, status=status.HTTP_200_OK)

class FinancialReportAPIView(APIView):
    """
    GET /api/admin/reports/financial/
    Consolidates transaction metrics, platform fee earnings, and payout breakdowns.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.user.user_type not in ['ADMIN', 'FINANCE']:
            return Response({"success": False, "message": "Acesso negado."}, status=status.HTTP_403_FORBIDDEN)

        # Revenue breakdown
        paid_payments = Payment.objects.filter(status='paid')
        total_payout = paid_payments.aggregate(models.Sum('amount'))['amount__sum'] or Decimal("0.00")
        platform_revenue = paid_payments.aggregate(models.Sum('platform_fee'))['platform_fee__sum'] or Decimal("0.00")
        driver_payouts = paid_payments.aggregate(models.Sum('driver_amount'))['driver_amount__sum'] or Decimal("0.00")

        method_counts = paid_payments.values('payment_method').annotate(
            count=models.Count('id'),
            total=models.Sum('amount')
        )

        data = {
            "total_payout": str(Decimal(total_payout).quantize(Decimal("0.01"))),
            "platform_earnings": str(Decimal(platform_revenue).quantize(Decimal("0.01"))),
            "driver_earnings": str(Decimal(driver_payouts).quantize(Decimal("0.01"))),
            "payment_methods": {
                item['payment_method']: {
                    "count": item['count'],
                    "total": str(Decimal(item['total']).quantize(Decimal("0.01")))
                } for item in method_counts
            }
        }

        return Response({
            "success": True,
            "data": data,
            "message": "Relatório financeiro gerado com sucesso."
        }, status=status.HTTP_200_OK)

class TrackingReportAPIView(APIView):
    """
    GET /api/admin/reports/tracking/
    Compiles anomalies like stops and route deviations.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.user.user_type not in ['ADMIN', 'SUPPORT', 'LOGISTICS']:
            return Response({"success": False, "message": "Acesso negado."}, status=status.HTTP_403_FORBIDDEN)

        total_stops = TrackingEvent.objects.filter(event_type='stop_detected').count()
        total_deviations = TrackingEvent.objects.filter(event_type='route_deviation').count()
        total_updates = TrackingEvent.objects.filter(event_type='location_updated').count()

        data = {
            "incidents": {
                "stops_detected": total_stops,
                "route_deviations": total_deviations,
                "telemetry_updates": total_updates
            }
        }

        return Response({
            "success": True,
            "data": data,
            "message": "Relatório de rastreamento e telemetria gerado."
        }, status=status.HTTP_200_OK)

from apps.ai_assistant.models import AIConversation, AIMessage
from apps.support.models import SupportTicket

class AIReportAPIView(APIView):
    """
    GET /api/admin/reports/ai/
    Generates statistics on AI assistant usage, conversation status,
    intent classification counts, and support ticket creation.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.user.user_type not in ['ADMIN', 'SUPPORT']:
            return Response({"success": False, "message": "Acesso negado."}, status=status.HTTP_403_FORBIDDEN)

        total_conversations = AIConversation.objects.count()
        escalated_conversations = AIConversation.objects.filter(status='escalated').count()
        closed_conversations = AIConversation.objects.filter(status='closed').count()
        active_conversations = AIConversation.objects.filter(status='active').count()

        total_messages = AIMessage.objects.count()
        avg_messages = (total_messages / total_conversations) if total_conversations > 0 else 0.0

        # Intent distribution
        intent_counts = AIMessage.objects.filter(sender='assistant').values('intent').annotate(count=models.Count('id'))
        intents_dict = {item['intent'] or 'unclassified': item['count'] for item in intent_counts}

        # Tickets created from AI assistant
        ai_tickets = SupportTicket.objects.filter(created_from='ai').count()

        data = {
            "total_conversations": total_conversations,
            "status_distribution": {
                "active": active_conversations,
                "closed": closed_conversations,
                "escalated": escalated_conversations
            },
            "average_messages_per_conversation": round(avg_messages, 2),
            "intent_distribution": intents_dict,
            "tickets_opened_by_ai": ai_tickets
        }

        return Response({
            "success": True,
            "data": data,
            "message": "Relatório analítico da IA gerado com sucesso."
        }, status=status.HTTP_200_OK)



# =====================================================================
# DJANGO PORTAL VIEWS (TEMPLATE-BASED MVP)
# =====================================================================

class PortalLoginView(LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.user_type in ['ADMIN', 'SUPPORT', 'LOGISTICS']:
            return redirect('operations-dashboard').url
        elif user.user_type == 'CARRIER':
            return redirect('carrier-dashboard').url
        else:
            return redirect('client-dashboard').url

class PortalLogoutView(LogoutView):
    next_page = 'portal-login'


class ClientDashboardView(LoginRequiredMixin, TemplateView):
    login_url = 'portal-login'
    template_name = 'core/client_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch active and past freights for this client
        context['freights'] = FreightOrder.objects.filter(customer=self.request.user)[:10]
        context['total_orders'] = FreightOrder.objects.filter(customer=self.request.user).count()
        context['pending_payments'] = Payment.objects.filter(payer=self.request.user, status='pending')
        return context

class ClientNewFreightView(LoginRequiredMixin, TemplateView):
    login_url = 'portal-login'
    template_name = 'core/client_new_freight.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cargo_types'] = CargoType.objects.filter(is_active=True)
        return context

class ClientTrackingView(LoginRequiredMixin, DetailView):
    login_url = 'portal-login'
    model = FreightOrder
    template_name = 'core/client_tracking.html'
    context_object_name = 'order'

    def get_queryset(self):
        return FreightOrder.objects.filter(customer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch historical events
        context['events'] = TrackingEvent.objects.filter(freight_order=self.object).order_by('-created_at')
        return context


class CarrierDashboardView(LoginRequiredMixin, TemplateView):
    login_url = 'portal-login'
    template_name = 'core/carrier_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Verify if user has a registered carrier company profile
        carrier = getattr(self.request.user, 'carrier_company', None)
        context['carrier'] = carrier
        if carrier:
            # Active associated vehicles and drivers
            context['drivers'] = DriverProfile.objects.filter(carrier_company=carrier)
            context['vehicles'] = Vehicle.objects.filter(carrier_company=carrier)
            context['freights'] = FreightOrder.objects.filter(carrier_company=carrier)[:10]
        else:
            context['drivers'] = []
            context['vehicles'] = []
            context['freights'] = []
        return context


class OperationsDashboardView(LoginRequiredMixin, TemplateView):
    login_url = 'portal-login'
    template_name = 'core/operations_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        # Strict operator verification
        if not request.user.is_superuser and request.user.user_type not in ['ADMIN', 'SUPPORT', 'LOGISTICS']:
            return redirect('portal-login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_orders'] = FreightOrder.objects.filter(
            status__in=[
                'requested', 'waiting_driver', 'driver_found', 'driver_going_to_pickup', 
                'arrived_at_origin', 'cargo_collected', 'in_transit', 'temporarily_stopped', 
                'route_deviation_detected', 'near_destination', 'arrived_at_destination'
            ]
        )[:15]
        context['recent_events'] = TrackingEvent.objects.filter(
            event_type__in=['stop_detected', 'route_deviation', 'occurrence_registered']
        )[:10]
        context['online_drivers'] = DriverProfile.objects.filter(is_online=True)
        return context

from apps.accounts.models import UserConsent

class AIChatPortalView(LoginRequiredMixin, TemplateView):
    login_url = 'portal-login'
    template_name = 'core/ai_chat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get or create the latest conversation for this user
        conversation = AIConversation.objects.filter(user=self.request.user, status='active').first()
        if not conversation:
            conversation = AIConversation.objects.create(user=self.request.user, channel='web')
        context['conversation'] = conversation
        context['messages'] = conversation.messages.all().order_by('created_at')
        context['tickets'] = SupportTicket.objects.filter(user=self.request.user)[:10]
        context['user_consents'] = UserConsent.objects.filter(user=self.request.user)
        return context


# =====================================================================
# PUBLIC PAGES & EXPERIENCES (MÓDULO 6)
# =====================================================================

class LandingView(TemplateView):
    template_name = 'core/landing.html'

class InvestorsView(TemplateView):
    template_name = 'core/investors.html'

class ProductView(TemplateView):
    template_name = 'core/product.html'

class TechnologyView(TemplateView):
    template_name = 'core/technology.html'

class SecurityView(TemplateView):
    template_name = 'core/security.html'


# =====================================================================
# DASHBOARDS & ANALYTICS VIEWS
# =====================================================================

class ExecutiveDashboardView(LoginRequiredMixin, TemplateView):
    login_url = 'portal-login'
    template_name = 'core/executive_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.user.user_type not in ['ADMIN', 'SUPPORT', 'LOGISTICS', 'FINANCE']:
            return redirect('portal-login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['metrics'] = ExecutiveMetricsService.get_metrics()
        return context


class LiveDemoView(LoginRequiredMixin, TemplateView):
    login_url = 'portal-login'
    template_name = 'core/live_demo.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.user.user_type not in ['ADMIN', 'SUPPORT', 'LOGISTICS']:
            return redirect('portal-login')
        return super().dispatch(request, *args, **kwargs)


# =====================================================================
# REST METRICS ENDPOINTS
# =====================================================================

from apps.core.metrics_services import (
    ExecutiveMetricsService, OperationalMetricsService,
    FinancialMetricsService, AIMetricsService
)

class ExecutiveMetricsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.user.user_type not in ['ADMIN', 'SUPPORT', 'FINANCE', 'LOGISTICS']:
            return Response({"success": False, "message": "Acesso negado."}, status=status.HTTP_403_FORBIDDEN)
        metrics = ExecutiveMetricsService.get_metrics()
        return Response({"success": True, "data": metrics}, status=status.HTTP_200_OK)


class OperationalMetricsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.user.user_type not in ['ADMIN', 'SUPPORT', 'LOGISTICS']:
            return Response({"success": False, "message": "Acesso negado."}, status=status.HTTP_403_FORBIDDEN)
        metrics = OperationalMetricsService.get_metrics()
        return Response({"success": True, "data": metrics}, status=status.HTTP_200_OK)


class FinancialMetricsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.user.user_type not in ['ADMIN', 'FINANCE']:
            return Response({"success": False, "message": "Acesso negado."}, status=status.HTTP_403_FORBIDDEN)
        metrics = FinancialMetricsService.get_metrics()
        return Response({"success": True, "data": metrics}, status=status.HTTP_200_OK)


class AIMetricsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser and request.user.user_type not in ['ADMIN', 'SUPPORT']:
            return Response({"success": False, "message": "Acesso negado."}, status=status.HTTP_403_FORBIDDEN)
        metrics = AIMetricsService.get_metrics()
        return Response({"success": True, "data": metrics}, status=status.HTTP_200_OK)


# =====================================================================
# PUBLIC FREIGHT SIMULATOR (RATE LIMITED)
# =====================================================================

from django.core.cache import cache
from apps.routing.services import RoutingService

class PublicFreightSimulatorAPIView(APIView):
    """
    POST /api/public/freight-simulator/
    Public calculator for freight price estimation and vehicle advice. Rate-limited by IP.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # Rate limit to 15 requests per minute per IP
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip:
            ip = ip.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')

        cache_key = f"rate_limit_freight_sim_{ip}"
        request_count = cache.get(cache_key, 0)
        if request_count >= 15:
            return Response({
                "success": False,
                "message": "Limite de simulação excedido. Aguarde 1 minuto para tentar novamente."
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        cache.set(cache_key, request_count + 1, 60)

        # Parse request inputs
        origin_lat = request.data.get('origin_latitude')
        origin_lng = request.data.get('origin_longitude')
        dest_lat = request.data.get('destination_latitude')
        dest_lng = request.data.get('destination_longitude')
        weight_kg = request.data.get('weight_kg')
        volume_m3 = request.data.get('volume_m3')
        cargo_category = request.data.get('cargo_category', 'equipamentos')
        requires_helper = request.data.get('requires_helper', False)
        requires_insurance = request.data.get('requires_insurance', False)

        if not all([origin_lat, origin_lng, dest_lat, dest_lng]):
            return Response({
                "success": False,
                "message": "Origem (lat, lng) e destino (lat, lng) são obrigatórios."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            origin_lat = Decimal(str(origin_lat))
            origin_lng = Decimal(str(origin_lng))
            dest_lat = Decimal(str(dest_lat))
            dest_lng = Decimal(str(dest_lng))
            weight_kg = Decimal(str(weight_kg or 0))
            volume_m3 = Decimal(str(volume_m3 or 0))
        except Exception:
            return Response({
                "success": False,
                "message": "Coordenadas, peso ou volume inválidos."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Calculate simulated distance and duration using standard routing logic
        route_data = RoutingService.calculate_simulated_route(origin_lat, origin_lng, dest_lat, dest_lng)
        distance_km = route_data['distance_km']
        duration_minutes = route_data['duration_minutes']

        # Recommended vehicle classification
        if cargo_category == 'graos':
            vehicle = 'Caminhão Graneleiro'
            body_type = 'Grade Alta com Lona'
        elif weight_kg > 10000 or volume_m3 > 40:
            vehicle = 'Carreta'
            body_type = 'Baú Fechado'
        elif weight_kg > 4000 or volume_m3 > 18:
            vehicle = 'Caminhão Médio (Toco)'
            body_type = 'Baú Fechado'
        elif weight_kg > 1500 or volume_m3 > 8:
            vehicle = 'Caminhão Pequeno (3/4)'
            body_type = 'Baú Fechado'
        elif volume_m3 > 3:
            vehicle = 'Van'
            body_type = 'Baú'
        else:
            vehicle = 'Fiorino / Utilitário'
            body_type = 'Baú Compacto'

        # Estimate pricing using platform logic
        base_fee = Decimal("45.00")
        distance_rate = Decimal("2.30")
        time_rate = Decimal("0.40")

        distance_fee = Decimal(str(distance_km)) * distance_rate
        time_fee = Decimal(str(duration_minutes)) * time_rate
        helper_fee = Decimal("100.00") if requires_helper else Decimal("0.00")
        insurance_fee = Decimal("35.00") if requires_insurance else Decimal("0.00")
        toll_fee = Decimal("18.00") if distance_km > 20 else Decimal("0.00")

        estimated_price = base_fee + distance_fee + time_fee + helper_fee + insurance_fee + toll_fee
        estimated_price = estimated_price.quantize(Decimal("0.01"))

        return Response({
            "success": True,
            "data": {
                "distance_km": float(distance_km),
                "duration_minutes": duration_minutes,
                "recommended_vehicle": vehicle,
                "recommended_body_type": body_type,
                "pricing": {
                    "base_fee": str(base_fee),
                    "distance_fee": str(distance_fee.quantize(Decimal("0.01"))),
                    "time_fee": str(time_fee.quantize(Decimal("0.01"))),
                    "helper_fee": str(helper_fee),
                    "insurance_fee": str(insurance_fee),
                    "toll_fee": str(toll_fee),
                    "total_estimated_price": str(estimated_price)
                }
            },
            "message": "Estimativa calculada com sucesso."
        }, status=status.HTTP_200_OK)

