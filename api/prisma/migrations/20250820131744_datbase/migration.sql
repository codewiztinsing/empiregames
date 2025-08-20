/*
  Warnings:

  - You are about to drop the column `code` on the `Game` table. All the data in the column will be lost.
  - Added the required column `betAmount` to the `Game` table without a default value. This is not possible if the table is not empty.
  - Added the required column `updatedAt` to the `Game` table without a default value. This is not possible if the table is not empty.

*/
-- DropIndex
DROP INDEX "public"."Game_code_key";

-- AlterTable
ALTER TABLE "public"."Game" DROP COLUMN "code",
ADD COLUMN     "betAmount" INTEGER NOT NULL,
ADD COLUMN     "updatedAt" TIMESTAMP(3) NOT NULL,
ADD COLUMN     "winnerId" INTEGER,
ALTER COLUMN "status" SET DEFAULT 'waiting';

-- CreateTable
CREATE TABLE "public"."_GamesPlayed" (
    "A" INTEGER NOT NULL,
    "B" INTEGER NOT NULL,

    CONSTRAINT "_GamesPlayed_AB_pkey" PRIMARY KEY ("A","B")
);

-- CreateIndex
CREATE INDEX "_GamesPlayed_B_index" ON "public"."_GamesPlayed"("B");

-- AddForeignKey
ALTER TABLE "public"."Game" ADD CONSTRAINT "Game_winnerId_fkey" FOREIGN KEY ("winnerId") REFERENCES "public"."Player"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."_GamesPlayed" ADD CONSTRAINT "_GamesPlayed_A_fkey" FOREIGN KEY ("A") REFERENCES "public"."Game"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."_GamesPlayed" ADD CONSTRAINT "_GamesPlayed_B_fkey" FOREIGN KEY ("B") REFERENCES "public"."Player"("id") ON DELETE CASCADE ON UPDATE CASCADE;
