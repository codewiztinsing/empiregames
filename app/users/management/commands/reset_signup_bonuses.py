from django.core.management.base import BaseCommand
from django.db import transaction, models
from users.models import User, ReferralBonus


class Command(BaseCommand):
    help = 'Reset all ReferralBonus records of type "signup" (Signup Bonus 10 birr)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--status',
            action='store_true',
            help='Show current status without making changes',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all signup bonuses',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt (use with caution)',
        )

    def handle(self, *args, **options):
        if options['status']:
            self.show_status()
        elif options['reset']:
            self.reset_bonuses(options['force'])
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Please specify --status or --reset. Use --help for more information."
                )
            )

    def show_status(self):
        """Show current status of signup bonuses"""
        self.stdout.write(
            self.style.SUCCESS("=" * 60)
        )
        self.stdout.write(
            self.style.SUCCESS("CURRENT STATUS OF SIGNUP BONUSES")
        )
        self.stdout.write(
            self.style.SUCCESS("=" * 60)
        )

        # Count signup bonuses
        signup_bonuses = ReferralBonus.objects.filter(bonus_type='signup')
        total_bonuses = signup_bonuses.count()

        self.stdout.write(f"Total signup bonuses: {total_bonuses}")

        if total_bonuses > 0:
            self.stdout.write("\nBreakdown by status:")
            for status, _ in ReferralBonus.STATUS_CHOICES:
                count = signup_bonuses.filter(status=status).count()
                self.stdout.write(f"  {status}: {count}")

            total_amount = signup_bonuses.aggregate(
                total=models.Sum('bonus_amount')
            )['total'] or 0
            self.stdout.write(f"\nTotal amount: {total_amount} ETB")

        # Count users with claimed flag
        users_with_claimed = User.objects.filter(signup_bonus_claimed=True).count()
        self.stdout.write(f"\nUsers with signup_bonus_claimed=True: {users_with_claimed}")

        self.stdout.write(
            self.style.SUCCESS("=" * 60)
        )

    def reset_bonuses(self, force=False):
        """Reset all signup bonuses"""
        self.stdout.write(
            self.style.SUCCESS("=" * 60)
        )
        self.stdout.write(
            self.style.SUCCESS("SIGNUP BONUS RESET SCRIPT")
        )
        self.stdout.write(
            self.style.SUCCESS("=" * 60)
        )

        try:
            # Count existing signup bonuses
            signup_bonuses = ReferralBonus.objects.filter(bonus_type='signup')
            total_bonuses = signup_bonuses.count()

            self.stdout.write(f"Found {total_bonuses} ReferralBonus records with type 'signup'")

            if total_bonuses == 0:
                self.stdout.write(
                    self.style.WARNING("No signup bonuses found. Nothing to reset.")
                )
                return

            # Show details of bonuses to be deleted
            self.stdout.write("\nBonuses to be deleted:")
            self.stdout.write("-" * 40)
            total_amount = 0
            for bonus in signup_bonuses:
                self.stdout.write(
                    f"ID: {bonus.id} | User: {bonus.referrer.username} | "
                    f"Amount: {bonus.bonus_amount} ETB | Status: {bonus.status}"
                )
                total_amount += bonus.bonus_amount

            self.stdout.write(f"\nTotal amount to be removed: {total_amount} ETB")

            # Count users with signup_bonus_claimed=True
            users_with_claimed_bonus = User.objects.filter(signup_bonus_claimed=True)
            users_count = users_with_claimed_bonus.count()

            self.stdout.write(f"\nFound {users_count} users with signup_bonus_claimed=True")

            # Confirm before proceeding (unless force is used)
            if not force:
                self.stdout.write("\n" + "=" * 60)
                self.stdout.write(
                    self.style.ERROR("WARNING: This action cannot be undone!")
                )
                self.stdout.write("=" * 60)

                confirm = input("\nDo you want to proceed? Type 'YES' to confirm: ")

                if confirm != 'YES':
                    self.stdout.write(
                        self.style.WARNING("Operation cancelled.")
                    )
                    return

            # Perform the reset operation
            with transaction.atomic():
                self.stdout.write("\nStarting reset operation...")

                # Delete all signup bonuses
                deleted_count, deleted_details = signup_bonuses.delete()
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Deleted {deleted_count} ReferralBonus records")
                )

                # Reset signup_bonus_claimed for all users
                updated_users = User.objects.filter(
                    signup_bonus_claimed=True
                ).update(signup_bonus_claimed=False)
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Reset signup_bonus_claimed flag for {updated_users} users")
                )

                self.stdout.write(
                    self.style.SUCCESS("\n✓ Reset operation completed successfully!")
                )

            # Final summary
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(
                self.style.SUCCESS("RESET SUMMARY")
            )
            self.stdout.write("=" * 60)
            self.stdout.write(f"• Deleted ReferralBonus records: {deleted_count}")
            self.stdout.write(f"• Reset user flags: {updated_users}")
            self.stdout.write(f"• Total amount removed: {total_amount} ETB")
            self.stdout.write(f"• Users affected: {users_count}")

            # Verify the reset
            remaining_bonuses = ReferralBonus.objects.filter(bonus_type='signup').count()
            remaining_users = User.objects.filter(signup_bonus_claimed=True).count()

            self.stdout.write(f"\nVerification:")
            self.stdout.write(f"• Remaining signup bonuses: {remaining_bonuses}")
            self.stdout.write(f"• Users with claimed flag still set: {remaining_users}")

            if remaining_bonuses == 0 and remaining_users == 0:
                self.stdout.write(
                    self.style.SUCCESS("\n✓ Reset completed successfully - all signup bonuses removed!")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("\n⚠ Warning: Some records may not have been reset properly.")
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Error during reset operation: {e}")
            )
            self.stdout.write("Transaction rolled back. No changes were made.")
            raise
