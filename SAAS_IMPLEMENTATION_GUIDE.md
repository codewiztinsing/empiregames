# SAAS Database Enhancement Implementation Guide

## Overview
This guide outlines the step-by-step implementation of the enhanced SAAS database architecture while preserving all existing functionality.

## Phase 1: Foundation Setup (Week 1-2)

### 1.1 Create New Apps
```bash
# Create new Django apps
python manage.py startapp tenants
python manage.py startapp finance
python manage.py startapp analytics
python manage.py startapp features
```

### 1.2 Update INSTALLED_APPS
```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Existing apps
    'users',
    'game',
    'wallet',
    'promotion',
    'referrals',
    'dashboard',
    'corsheaders',
    
    # New SAAS apps
    'tenants',
    'finance',
    'analytics',
    'features',
]
```

### 1.3 Create Initial Migrations
```bash
# Create migrations for new models
python manage.py makemigrations tenants
python manage.py makemigrations finance
python manage.py makemigrations analytics
python manage.py makemigrations features
```

## Phase 2: Multi-Tenancy Implementation (Week 2-3)

### 2.1 Create Default Tenant
```python
# management/commands/create_default_tenant.py
from django.core.management.base import BaseCommand
from tenants.models import Tenant, TenantSettings, SubscriptionPlan, TenantSubscription

class Command(BaseCommand):
    help = 'Create default tenant for existing data'

    def handle(self, *args, **options):
        # Create default tenant
        default_tenant = Tenant.objects.create(
            name='Default Gaming Platform',
            slug='default',
            is_active=True,
            is_trial=False,
            company_name='Empire Games',
            contact_email='admin@empiregames.com',
            currency='ETB',
            language='en',
            timezone='Africa/Addis_Ababa'
        )
        
        # Create tenant settings
        TenantSettings.objects.create(
            tenant=default_tenant,
            default_entry_fee=10.00,
            max_fake_players=50,
            fake_player_threshold=10,
            house_edge_percentage=22.00,
            min_withdrawal=50.00,
            max_withdrawal=10000.00,
            referral_bonus_percentage=10.00,
            signup_bonus_amount=0.00
        )
        
        # Create default subscription plan
        plan = SubscriptionPlan.objects.create(
            name='Default Plan',
            plan_type='basic',
            billing_cycle='monthly',
            price=0.00,
            currency='USD',
            max_users=1000,
            max_games_per_day=10000,
            max_storage_gb=100,
            features={
                'fake_players': True,
                'promotions': True,
                'analytics': True,
                'api_access': True
            }
        )
        
        # Create tenant subscription
        TenantSubscription.objects.create(
            tenant=default_tenant,
            plan=plan,
            status='active',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timezone.timedelta(days=30),
            next_billing_date=timezone.now() + timezone.timedelta(days=30)
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created default tenant: {default_tenant.name}')
        )
```

### 2.2 Add Tenant Field to Existing Models
```python
# Create migration to add tenant field to existing models
# users/migrations/XXXX_add_tenant_to_user.py
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('users', 'XXXX_previous_migration'),
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='tenant',
            field=models.ForeignKey(
                default=1,  # Default to first tenant
                on_delete=django.db.models.deletion.CASCADE,
                related_name='users',
                to='tenants.tenant'
            ),
            preserve_default=False,
        ),
    ]
```

### 2.3 Update Existing Models
```python
# users/models.py - Add tenant field
class User(AbstractUser):
    # ... existing fields ...
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='users')
    
    class Meta:
        # ... existing meta ...
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            # ... existing indexes ...
        ]

# wallet/models.py - Add tenant field
class Wallet(models.Model):
    # ... existing fields ...
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='wallets')
    
    class Meta:
        unique_together = ['tenant', 'user']

# game/models.py - Add tenant field
class Game(models.Model):
    # ... existing fields ...
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='games')
    
    class Meta:
        unique_together = ['tenant', 'game_number']
```

## Phase 3: Financial System Migration (Week 3-4)

### 3.1 Create Account Migration
```python
# finance/management/commands/migrate_to_accounts.py
from django.core.management.base import BaseCommand
from finance.models import Account, Transaction
from wallet.models import Wallet as OldWallet
from users.models import User

class Command(BaseCommand):
    help = 'Migrate existing wallet data to new account system'

    def handle(self, *args, **options):
        # Create user wallet accounts
        for user in User.objects.all():
            # Create user wallet account
            wallet_account = Account.objects.create(
                tenant=user.tenant,
                user=user,
                account_type='user_wallet',
                name=f"{user.username} Wallet",
                balance=user.wallet.balance if hasattr(user, 'wallet') else 0.00,
                currency='ETB'
            )
            
            # Create house account for tenant
            house_account, created = Account.objects.get_or_create(
                tenant=user.tenant,
                account_type='house_account',
                defaults={
                    'name': f"{user.tenant.name} House Account",
                    'balance': 0.00,
                    'currency': 'ETB'
                }
            )
            
            self.stdout.write(f'Created account for {user.username}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully migrated wallet data to account system')
        )
```

### 3.2 Migrate Transactions
```python
# finance/management/commands/migrate_transactions.py
from django.core.management.base import BaseCommand
from finance.models import Account, Transaction
from wallet.models import Transaction as OldTransaction

class Command(BaseCommand):
    help = 'Migrate existing transactions to new transaction system'

    def handle(self, *args, **options):
        for old_transaction in OldTransaction.objects.all():
            # Get user's wallet account
            user_account = Account.objects.get(
                tenant=old_transaction.user.tenant,
                user=old_transaction.user,
                account_type='user_wallet'
            )
            
            # Get house account
            house_account = Account.objects.get(
                tenant=old_transaction.user.tenant,
                account_type='house_account'
            )
            
            # Create new transaction based on type
            if old_transaction.type == 'DEPOSIT':
                Transaction.objects.create(
                    tenant=old_transaction.user.tenant,
                    transaction_type='deposit',
                    status='completed' if old_transaction.status == 'success' else old_transaction.status,
                    debit_account=user_account,
                    credit_account=house_account,
                    amount=old_transaction.amount,
                    user=old_transaction.user,
                    reference=old_transaction.reference,
                    description=f"Migrated {old_transaction.type} transaction",
                    processed_at=old_transaction.created_at
                )
            elif old_transaction.type == 'WITHDRAW':
                Transaction.objects.create(
                    tenant=old_transaction.user.tenant,
                    transaction_type='withdrawal',
                    status='completed' if old_transaction.status == 'success' else old_transaction.status,
                    debit_account=house_account,
                    credit_account=user_account,
                    amount=old_transaction.amount,
                    user=old_transaction.user,
                    reference=old_transaction.reference,
                    description=f"Migrated {old_transaction.type} transaction",
                    processed_at=old_transaction.created_at
                )
            # ... handle other transaction types
        
        self.stdout.write(
            self.style.SUCCESS('Successfully migrated transactions')
        )
```

## Phase 4: Enhanced Game System (Week 4-5)

### 4.1 Create Game Rooms
```python
# game/management/commands/create_game_rooms.py
from django.core.management.base import BaseCommand
from game.models import GameRoom
from tenants.models import Tenant

class Command(BaseCommand):
    help = 'Create default game rooms for tenants'

    def handle(self, *args, **options):
        for tenant in Tenant.objects.all():
            # Create standard game rooms
            GameRoom.objects.create(
                tenant=tenant,
                name='Standard Room',
                room_type='standard',
                entry_fee=10.00,
                max_players=100,
                min_players=1
            )
            
            GameRoom.objects.create(
                tenant=tenant,
                name='Premium Room',
                room_type='premium',
                entry_fee=50.00,
                max_players=50,
                min_players=1
            )
            
            GameRoom.objects.create(
                tenant=tenant,
                name='VIP Room',
                room_type='vip',
                entry_fee=100.00,
                max_players=25,
                min_players=1
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created game rooms')
        )
```

### 4.2 Migrate Existing Games
```python
# game/management/commands/migrate_games.py
from django.core.management.base import BaseCommand
from game.models import Game as NewGame, GameRoom
from game.models import Game as OldGame

class Command(BaseCommand):
    help = 'Migrate existing games to new game system'

    def handle(self, *args, **options):
        for old_game in OldGame.objects.all():
            # Get appropriate game room
            game_room = GameRoom.objects.filter(
                tenant=old_game.tenant,
                entry_fee=old_game.entry_fee
            ).first()
            
            if not game_room:
                game_room = GameRoom.objects.create(
                    tenant=old_game.tenant,
                    name=f'Room {old_game.entry_fee}',
                    entry_fee=old_game.entry_fee,
                    max_players=100
                )
            
            # Create new game
            new_game = NewGame.objects.create(
                tenant=old_game.tenant,
                room=game_room,
                game_number=old_game.id,  # Use old ID as game number
                status=old_game.status,
                total_players=old_game.total_players,
                real_players=old_game.real_players,
                fake_players=old_game.fake_players,
                total_entry_fees=old_game.total_players * old_game.entry_fee,
                prize_pool=old_game.total_win_amount,
                winner=old_game.winner,
                started_at=old_game.started_at,
                ended_at=old_game.ended_at,
                created_at=old_game.created_at
            )
            
            self.stdout.write(f'Migrated game {old_game.id} to {new_game.id}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully migrated games')
        )
```

## Phase 5: Analytics and Monitoring (Week 5-6)

### 5.1 Create Analytics Setup
```python
# analytics/management/commands/setup_analytics.py
from django.core.management.base import BaseCommand
from analytics.models import UserAnalytics
from users.models import User

class Command(BaseCommand):
    help = 'Setup analytics for existing users'

    def handle(self, *args, **options):
        for user in User.objects.all():
            UserAnalytics.objects.create(
                user=user,
                total_games_played=user.total_games_played,
                total_games_won=0,  # Calculate from games
                total_bet_amount=0,  # Calculate from transactions
                total_win_amount=0,  # Calculate from transactions
                total_deposits=0,  # Calculate from transactions
                total_withdrawals=0,  # Calculate from transactions
                total_referrals=user.referrals.count(),
                referral_earnings=user.total_referral_earnings
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully setup user analytics')
        )
```

### 5.2 Create Audit Logging Middleware
```python
# analytics/middleware.py
from django.utils.deprecation import MiddlewareMixin
from analytics.models import AuditLog, PerformanceLog
import time
import json

class AuditMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._audit_start_time = time.time()
        request._audit_data = {
            'method': request.method,
            'path': request.path,
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        }

    def process_response(self, request, response):
        if hasattr(request, '_audit_start_time'):
            response_time = int((time.time() - request._audit_start_time) * 1000)
            
            # Log performance
            PerformanceLog.objects.create(
                tenant=getattr(request, 'tenant', None),
                endpoint=request.path,
                method=request.method,
                response_time=response_time,
                status_code=response.status_code,
                user=getattr(request, 'user', None) if request.user.is_authenticated else None,
                ip_address=request._audit_data['ip_address'],
                user_agent=request._audit_data['user_agent']
            )
        
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
```

## Phase 6: Feature Flags and Limits (Week 6-7)

### 6.1 Create Default Feature Flags
```python
# features/management/commands/setup_feature_flags.py
from django.core.management.base import BaseCommand
from features.models import FeatureFlag, UsageLimit
from tenants.models import Tenant

class Command(BaseCommand):
    help = 'Setup default feature flags and usage limits'

    def handle(self, *args, **options):
        for tenant in Tenant.objects.all():
            # Create default feature flags
            FeatureFlag.objects.create(
                tenant=tenant,
                name='fake_players_enabled',
                description='Enable fake players in games',
                flag_type='boolean',
                boolean_value=True
            )
            
            FeatureFlag.objects.create(
                tenant=tenant,
                name='promotions_enabled',
                description='Enable promotion system',
                flag_type='boolean',
                boolean_value=True
            )
            
            FeatureFlag.objects.create(
                tenant=tenant,
                name='max_fake_players',
                description='Maximum number of fake players',
                flag_type='number',
                number_value=50
            )
            
            # Create usage limits
            UsageLimit.objects.create(
                tenant=tenant,
                resource_type='games',
                limit_type='daily',
                limit_value=1000,
                next_reset=timezone.now() + timezone.timedelta(days=1)
            )
            
            UsageLimit.objects.create(
                tenant=tenant,
                resource_type='users',
                limit_type='total',
                limit_value=1000
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully setup feature flags and limits')
        )
```

## Phase 7: Security and Performance (Week 7-8)

### 7.1 Add Database Indexes
```python
# Create migration for additional indexes
# analytics/migrations/XXXX_add_performance_indexes.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('analytics', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_tenant_action ON analytics_auditlog (tenant_id, action_type);",
            reverse_sql="DROP INDEX IF EXISTS idx_audit_logs_tenant_action;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_logs_timestamp ON analytics_performancelog (timestamp);",
            reverse_sql="DROP INDEX IF EXISTS idx_performance_logs_timestamp;"
        ),
    ]
```

### 7.2 Add Row-Level Security
```python
# tenants/management/commands/setup_rls.py
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Setup Row-Level Security for multi-tenancy'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Enable RLS on key tables
            tables = [
                'users_user',
                'finance_account',
                'finance_transaction',
                'game_game',
                'promotion_promotion',
            ]
            
            for table in tables:
                cursor.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
                cursor.execute(f"""
                    CREATE POLICY tenant_isolation ON {table}
                    FOR ALL TO PUBLIC
                    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
                """)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully setup Row-Level Security')
        )
```

## Testing Strategy

### 1. Unit Tests
```python
# tests/test_tenant_isolation.py
from django.test import TestCase
from tenants.models import Tenant
from users.models import User

class TenantIsolationTest(TestCase):
    def setUp(self):
        self.tenant1 = Tenant.objects.create(name='Tenant 1', slug='tenant1')
        self.tenant2 = Tenant.objects.create(name='Tenant 2', slug='tenant2')
        
        self.user1 = User.objects.create_user(
            username='user1',
            tenant=self.tenant1
        )
        self.user2 = User.objects.create_user(
            username='user2',
            tenant=self.tenant2
        )
    
    def test_tenant_isolation(self):
        # Users should only see their tenant's data
        tenant1_users = User.objects.filter(tenant=self.tenant1)
        tenant2_users = User.objects.filter(tenant=self.tenant2)
        
        self.assertEqual(tenant1_users.count(), 1)
        self.assertEqual(tenant2_users.count(), 1)
        self.assertNotEqual(tenant1_users.first(), tenant2_users.first())
```

### 2. Integration Tests
```python
# tests/test_financial_system.py
from django.test import TestCase
from finance.models import Account, Transaction
from tenants.models import Tenant
from users.models import User

class FinancialSystemTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='Test Tenant', slug='test')
        self.user = User.objects.create_user(
            username='testuser',
            tenant=self.tenant
        )
        
        self.user_account = Account.objects.create(
            tenant=self.tenant,
            user=self.user,
            account_type='user_wallet',
            balance=100.00
        )
        
        self.house_account = Account.objects.create(
            tenant=self.tenant,
            account_type='house_account',
            balance=0.00
        )
    
    def test_deposit_transaction(self):
        transaction = Transaction.objects.create(
            tenant=self.tenant,
            transaction_type='deposit',
            debit_account=self.user_account,
            credit_account=self.house_account,
            amount=50.00,
            user=self.user
        )
        
        transaction.process()
        
        self.user_account.refresh_from_db()
        self.house_account.refresh_from_db()
        
        self.assertEqual(self.user_account.balance, 150.00)
        self.assertEqual(self.house_account.balance, 50.00)
```

## Deployment Checklist

### Pre-Deployment
- [ ] Backup existing database
- [ ] Test migrations on staging environment
- [ ] Verify all existing functionality works
- [ ] Run comprehensive test suite
- [ ] Performance testing

### Deployment Steps
1. Deploy new code with migrations disabled
2. Run migrations during maintenance window
3. Run data migration commands
4. Verify data integrity
5. Enable new features gradually
6. Monitor performance and errors

### Post-Deployment
- [ ] Monitor system performance
- [ ] Check error logs
- [ ] Verify tenant isolation
- [ ] Test financial calculations
- [ ] Monitor user experience

## Rollback Plan

### If Issues Occur
1. Disable new features via feature flags
2. Revert to old API endpoints
3. Restore database from backup if necessary
4. Investigate and fix issues
5. Re-deploy when ready

This implementation plan ensures a smooth transition to the SAAS architecture while preserving all existing functionality and providing a robust foundation for future growth.
