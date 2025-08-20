/*
  Warnings:

  - You are about to drop the column `gameId` on the `Player` table. All the data in the column will be lost.
  - You are about to drop the column `name` on the `Player` table. All the data in the column will be lost.
  - Added the required column `balance` to the `Player` table without a default value. This is not possible if the table is not empty.
  - Added the required column `phoneNumber` to the `Player` table without a default value. This is not possible if the table is not empty.
  - Added the required column `telegramId` to the `Player` table without a default value. This is not possible if the table is not empty.
  - Added the required column `username` to the `Player` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE "public"."Player" DROP CONSTRAINT "Player_gameId_fkey";

-- AlterTable
ALTER TABLE "public"."Player" DROP COLUMN "gameId",
DROP COLUMN "name",
ADD COLUMN     "balance" INTEGER NOT NULL,
ADD COLUMN     "joinedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN     "phoneNumber" TEXT NOT NULL,
ADD COLUMN     "telegramId" TEXT NOT NULL,
ADD COLUMN     "username" TEXT NOT NULL;
