-- Add unique constraint to telegramId field
ALTER TABLE "Player" ADD CONSTRAINT "Player_telegramId_key" UNIQUE ("telegramId");
