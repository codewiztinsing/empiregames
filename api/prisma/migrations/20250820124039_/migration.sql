/*
  Warnings:

  - The primary key for the `Game` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - You are about to drop the column `callIntervalMs` on the `Game` table. All the data in the column will be lost.
  - You are about to drop the column `currentIndex` on the `Game` table. All the data in the column will be lost.
  - You are about to drop the column `endedAt` on the `Game` table. All the data in the column will be lost.
  - You are about to drop the column `numbers` on the `Game` table. All the data in the column will be lost.
  - You are about to drop the column `roomId` on the `Game` table. All the data in the column will be lost.
  - You are about to drop the column `startedAt` on the `Game` table. All the data in the column will be lost.
  - The `id` column on the `Game` table would be dropped and recreated. This will lead to data loss if there is data in the column.
  - The primary key for the `Player` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - You are about to drop the column `joinedAt` on the `Player` table. All the data in the column will be lost.
  - You are about to drop the column `roomId` on the `Player` table. All the data in the column will be lost.
  - You are about to drop the column `socketId` on the `Player` table. All the data in the column will be lost.
  - You are about to drop the column `userId` on the `Player` table. All the data in the column will be lost.
  - The `id` column on the `Player` table would be dropped and recreated. This will lead to data loss if there is data in the column.
  - You are about to drop the `Call` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `Card` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `GameRoom` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `User` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `Win` table. If the table is not empty, all the data it contains will be lost.
  - A unique constraint covering the columns `[code]` on the table `Game` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `code` to the `Game` table without a default value. This is not possible if the table is not empty.
  - Added the required column `status` to the `Game` table without a default value. This is not possible if the table is not empty.
  - Added the required column `gameId` to the `Player` table without a default value. This is not possible if the table is not empty.
  - Added the required column `name` to the `Player` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE "public"."Call" DROP CONSTRAINT "Call_gameId_fkey";

-- DropForeignKey
ALTER TABLE "public"."Card" DROP CONSTRAINT "Card_playerId_fkey";

-- DropForeignKey
ALTER TABLE "public"."Game" DROP CONSTRAINT "Game_roomId_fkey";

-- DropForeignKey
ALTER TABLE "public"."GameRoom" DROP CONSTRAINT "GameRoom_ownerId_fkey";

-- DropForeignKey
ALTER TABLE "public"."Player" DROP CONSTRAINT "Player_roomId_fkey";

-- DropForeignKey
ALTER TABLE "public"."Player" DROP CONSTRAINT "Player_userId_fkey";

-- DropForeignKey
ALTER TABLE "public"."Win" DROP CONSTRAINT "Win_gameId_fkey";

-- DropForeignKey
ALTER TABLE "public"."Win" DROP CONSTRAINT "Win_playerId_fkey";

-- DropIndex
DROP INDEX "public"."Game_roomId_key";

-- DropIndex
DROP INDEX "public"."Player_userId_roomId_key";

-- AlterTable
ALTER TABLE "public"."Game" DROP CONSTRAINT "Game_pkey",
DROP COLUMN "callIntervalMs",
DROP COLUMN "currentIndex",
DROP COLUMN "endedAt",
DROP COLUMN "numbers",
DROP COLUMN "roomId",
DROP COLUMN "startedAt",
ADD COLUMN     "code" TEXT NOT NULL,
ADD COLUMN     "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN     "status" TEXT NOT NULL,
DROP COLUMN "id",
ADD COLUMN     "id" SERIAL NOT NULL,
ADD CONSTRAINT "Game_pkey" PRIMARY KEY ("id");

-- AlterTable
ALTER TABLE "public"."Player" DROP CONSTRAINT "Player_pkey",
DROP COLUMN "joinedAt",
DROP COLUMN "roomId",
DROP COLUMN "socketId",
DROP COLUMN "userId",
ADD COLUMN     "gameId" INTEGER NOT NULL,
ADD COLUMN     "name" TEXT NOT NULL,
DROP COLUMN "id",
ADD COLUMN     "id" SERIAL NOT NULL,
ADD CONSTRAINT "Player_pkey" PRIMARY KEY ("id");

-- DropTable
DROP TABLE "public"."Call";

-- DropTable
DROP TABLE "public"."Card";

-- DropTable
DROP TABLE "public"."GameRoom";

-- DropTable
DROP TABLE "public"."User";

-- DropTable
DROP TABLE "public"."Win";

-- DropEnum
DROP TYPE "public"."RoomStatus";

-- CreateTable
CREATE TABLE "public"."Winner" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "gameCode" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Winner_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Game_code_key" ON "public"."Game"("code");

-- AddForeignKey
ALTER TABLE "public"."Player" ADD CONSTRAINT "Player_gameId_fkey" FOREIGN KEY ("gameId") REFERENCES "public"."Game"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
