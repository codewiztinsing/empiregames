/*
  Warnings:

  - You are about to drop the `Deposit` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `Withdrawal` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "public"."Deposit" DROP CONSTRAINT "Deposit_playerId_fkey";

-- DropForeignKey
ALTER TABLE "public"."Withdrawal" DROP CONSTRAINT "Withdrawal_playerId_fkey";

-- DropTable
DROP TABLE "public"."Deposit";

-- DropTable
DROP TABLE "public"."Withdrawal";

-- CreateTable
CREATE TABLE "public"."PaymentReceiverDetails" (
    "id" SERIAL NOT NULL,
    "phoneNumber" TEXT,
    "accountNumber" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "PaymentReceiverDetails_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."PaymentRequest" (
    "id" SERIAL NOT NULL,
    "playerId" INTEGER NOT NULL,
    "amount" DOUBLE PRECISION NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "txRef" TEXT,
    "phoneNumber" TEXT,
    "accountNumber" TEXT,
    "bankName" TEXT,
    "reason" TEXT,
    "processedBy" INTEGER,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "PaymentRequest_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."PaymentSession" (
    "id" SERIAL NOT NULL,
    "playerId" INTEGER NOT NULL,
    "amount" DOUBLE PRECISION NOT NULL,
    "txRef" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "paymentMethod" TEXT NOT NULL,
    "sessionData" JSONB,
    "expiresAt" TIMESTAMP(3),
    "completedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "PaymentSession_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "PaymentRequest_txRef_key" ON "public"."PaymentRequest"("txRef");

-- CreateIndex
CREATE UNIQUE INDEX "PaymentSession_txRef_key" ON "public"."PaymentSession"("txRef");

-- AddForeignKey
ALTER TABLE "public"."PaymentRequest" ADD CONSTRAINT "PaymentRequest_playerId_fkey" FOREIGN KEY ("playerId") REFERENCES "public"."Player"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."PaymentSession" ADD CONSTRAINT "PaymentSession_playerId_fkey" FOREIGN KEY ("playerId") REFERENCES "public"."Player"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
