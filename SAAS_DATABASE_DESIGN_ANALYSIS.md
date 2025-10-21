# Database Design Analysis & SAAS Improvement Suggestions

## Current Database Structure Analysis

### Apps and Models Overview:
1. **users** - User management, referrals, withdrawals
2. **game** - Game sessions, settings, fake players
3. **wallet** - Financial transactions, balances
4. **promotion** - Marketing campaigns
5. **referrals** - Referral system (duplicate functionality)
6. **webhooks** - External integrations
7. **dashboard** - Admin interface

## Critical Issues Identified

### 1. **Data Duplication & Inconsistency**
- `WithdrawalRequest` exists in both `users` and `wallet` apps
- `ReferralBonus` exists in both `users` and `referrals` apps
- Game statistics scattered across multiple models
- Inconsistent field types (FloatField vs DecimalField)

### 2. **Missing SAAS Architecture**
- No multi-tenancy support
- No organization/tenant isolation
- No subscription/billing models
- No feature flags or plan limitations

### 3. **Scalability Issues**
- No database partitioning
- Missing indexes on frequently queried fields
- No caching strategy
- No read replicas consideration

### 4. **Security Concerns**
- No audit trails
- No soft deletes
- No data encryption at rest
- No role-based access control (RBAC)

## SAAS Database Design Recommendations

### 1. **Multi-Tenancy Architecture**

#### Option A: Database per Tenant (Recommended for your use case)
```python
# New app: tenants
class Tenant(models.Model):
    name = models.CharField(max_length=100)
    subdomain = models.CharField(max_length=50, unique=True)
    database_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    subscription_plan = models.ForeignKey('SubscriptionPlan', on_delete=models.CASCADE)
    
class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)
    max_users = models.IntegerField()
    max_games_per_day = models.IntegerField()
    features = models.JSONField(default=dict)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
```

#### Option B: Shared Database with Tenant Isolation
```python
# Add to all models
class TenantAwareModel(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    
    class Meta:
        abstract = True

# Update existing models
class User(TenantAwareModel, AbstractUser):
    # existing fields...
    pass
```

### 2. **Unified Financial System**

```python
# New app: finance
class Account(models.Model):
    ACCOUNT_TYPES = [
        ('user_wallet', 'User Wallet'),
        ('referral_bonus', 'Referral Bonus'),
        ('game_pool', 'Game Pool'),
        ('commission', 'Commission'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='ETB')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('bet', 'Bet'),
        ('win', 'Win'),
        ('referral_bonus', 'Referral Bonus'),
        ('commission', 'Commission'),
        ('refund', 'Refund'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='outgoing_transactions')
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='incoming_transactions')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reference = models.CharField(max_length=100, blank=True, null=True)
    metadata = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
```

### 3. **Enhanced User Management**

```python
# Updated users/models.py
class User(AbstractUser):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    telegram_id = models.CharField(max_length=15)
    referral_code = models.CharField(max_length=15, unique=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    # User preferences
    preferences = models.JSONField(default=dict)
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    
    # Status tracking
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
```

### 4. **Audit Trail System**

```python
# New app: audit
class AuditLog(models.Model):
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('transaction', 'Transaction'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    old_values = models.JSONField(default=dict)
    new_values = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['tenant', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['model_name', 'object_id']),
        ]
```

### 5. **Feature Flags & Limits**

```python
# New app: features
class FeatureFlag(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_enabled = models.BooleanField(default=False)
    config = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UsageLimit(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    limit_type = models.CharField(max_length=50)  # 'daily_games', 'monthly_transactions'
    current_usage = models.IntegerField(default=0)
    limit_value = models.IntegerField()
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### 6. **Improved Game System**

```python
# Updated game/models.py
class GameRoom(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2)
    max_players = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)
    settings = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

class Game(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('waiting', 'Waiting'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='waiting')
    
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    total_players = models.IntegerField(default=0)
    total_pool = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    winner_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PlayerGame(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    selected_numbers = models.JSONField(default=list)
    is_winner = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
```

### 7. **Database Indexes & Performance**

```python
# Add to all models with frequent queries
class Meta:
    indexes = [
        models.Index(fields=['tenant', 'created_at']),
        models.Index(fields=['user', 'created_at']),
        models.Index(fields=['status', 'created_at']),
        # Add composite indexes based on query patterns
    ]
```

### 8. **Caching Strategy**

```python
# New app: cache
class CacheKey(models.Model):
    key = models.CharField(max_length=200, unique=True)
    value = models.TextField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['expires_at']),
        ]
```

## Migration Strategy

### Phase 1: Foundation (Week 1-2)
1. Create `tenants` app
2. Add tenant field to existing models
3. Create audit logging system
4. Implement soft deletes

### Phase 2: Financial System (Week 3-4)
1. Create unified `finance` app
2. Migrate existing wallet/transaction data
3. Implement double-entry bookkeeping
4. Add currency support

### Phase 3: Features & Limits (Week 5-6)
1. Implement feature flags
2. Add usage tracking
3. Create subscription management
4. Add billing integration

### Phase 4: Performance & Security (Week 7-8)
1. Add database indexes
2. Implement caching layer
3. Add encryption for sensitive data
4. Performance optimization

## Database Configuration Recommendations

### PostgreSQL Settings for SAAS
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'empiregames_saas',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'CONN_MAX_AGE': 600,
        }
    }
}

# Connection pooling
DATABASE_CONNECTION_POOL_SIZE = 20
DATABASE_CONNECTION_MAX_AGE = 600
```

### Redis Configuration
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        }
    }
}
```

## Security Enhancements

### 1. Data Encryption
```python
from django_cryptography.fields import encrypt

class SensitiveData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    encrypted_data = encrypt(models.TextField())
```

### 2. Row-Level Security (PostgreSQL)
```sql
-- Enable RLS on all tenant-aware tables
ALTER TABLE users_user ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON users_user 
    FOR ALL TO app_user 
    USING (tenant_id = current_setting('app.current_tenant_id')::int);
```

### 3. API Rate Limiting
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

## Monitoring & Analytics

### 1. Database Monitoring
```python
# New app: monitoring
class DatabaseMetrics(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
class PerformanceLog(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=200)
    response_time = models.FloatField()
    status_code = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

### 2. Business Intelligence
```python
# New app: analytics
class UserAnalytics(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    metric_date = models.DateField()
    games_played = models.IntegerField(default=0)
    total_wagered = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_won = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    login_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['tenant', 'user', 'metric_date']
        indexes = [
            models.Index(fields=['tenant', 'metric_date']),
            models.Index(fields=['user', 'metric_date']),
        ]
```

## Implementation Priority

### High Priority (Immediate)
1. **Multi-tenancy** - Critical for SAAS
2. **Audit logging** - Compliance requirement
3. **Unified financial system** - Data integrity
4. **Database indexes** - Performance

### Medium Priority (Next 4 weeks)
1. **Feature flags** - Business flexibility
2. **Caching layer** - Performance
3. **Soft deletes** - Data safety
4. **API rate limiting** - Security

### Low Priority (Future)
1. **Advanced analytics** - Business intelligence
2. **Machine learning** - Predictive features
3. **Multi-currency** - International expansion
4. **Advanced reporting** - Business insights

This comprehensive redesign will transform your current gaming platform into a robust, scalable SAAS application with proper multi-tenancy, security, and performance optimizations.
