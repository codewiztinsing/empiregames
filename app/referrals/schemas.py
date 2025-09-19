from ninja import Schema
from decimal import Decimal
from datetime import datetime
from typing import List, Optional

class ReferralBonusSchema(Schema):
    id: int
    from_user_username: str
    generation: int
    win_amount: Decimal
    bonus_percentage: Decimal
    bonus_amount: Decimal
    game_id: Optional[str]
    status: str
    created_at: datetime

class ReferralWithdrawalSchema(Schema):
    id: int
    amount: Decimal
    status: str
    created_at: datetime
    processed_at: Optional[datetime]
    notes: Optional[str]

class WithdrawalRequestSchema(Schema):
    amount: Decimal

class ReferralUserSchema(Schema):
    username: str
    phone: str
    telegram_id: str
    created_at: datetime
    is_agent: bool

class ReferralTreeItemSchema(Schema):
    user: ReferralUserSchema
    generation: int
    referrals: List['ReferralTreeItemSchema']

class ReferralTreeSchema(Schema):
    referrals: List[ReferralTreeItemSchema]

class UserStatsSchema(Schema):
    games_played_today: int
    games_played_this_week: int
    total_games_played: int
    total_winnings: Decimal
    total_referral_bonus: Decimal
    available_balance: Decimal
    can_withdraw: bool
    referral_code: str
    is_agent: bool
