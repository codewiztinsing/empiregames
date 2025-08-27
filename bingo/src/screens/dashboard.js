import React, { useState } from "react";
import DashboardComponet from "../components/dashboardcomponet";  
import GameTypes from "../components/GameTypes";
import Games from "../components/Games";
import Transactions from "../components/Transactions";
import Players from "../components/Players";
import Referrals from "../components/Referrals";
import Payments from "../components/Payments";
import Logout from "../components/Logout";
import Messages from "../components/Messages";
import ContactInfo from "../components/ContactInfo";
import { Home, Grid3X3, Grid, Gamepad2, CreditCard, ArrowLeftRight, Users, UserPlus, MessageSquare, Phone, LogOut, Menu, X } from "lucide-react";
import BingoCard from "../components/BingoCard";
 function Dashboard() {
    const [display, setDisplay] = useState("dashboard");

    
  return (
    <div className="flex w-full h-screen bg-gray-900 text-white overflow-hidden">
      {/* Mobile Menu Button */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <button
          onClick={() => setDisplay(display === "menu" ? "dashboard" : "menu")}
          className="bg-gray-800 p-2 rounded-lg"
        >
          {display === "menu" ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Sidebar */}
      <aside className={`${
        display === "menu" ? "translate-x-0" : "-translate-x-full"
      } md:translate-x-0 fixed md:relative z-40 w-64 bg-gray-800 p-4 flex flex-col transition-transform duration-300 ease-in-out h-full overflow-y-auto`}>
        <h2 className="text-xl font-bold mb-6 mt-12 md:mt-0">Bingo Admin</h2>
        <nav className="space-y-2">
          <button className={`w-full text-left px-4 py-2 ${display === "dashboard" ? "bg-gray-700" : "hover:bg-gray-700"} rounded-lg flex items-center gap-2`} onClick={() => setDisplay("dashboard")}>
            <Home className="w-4 h-4" />
            Dashboard
          </button>
          <button className={`w-full text-left px-4 py-2 ${display === "game-types" ? "bg-gray-700" : "hover:bg-gray-700"} rounded-lg flex items-center gap-2`} onClick={() => setDisplay("game-types")}>
            <Grid3X3 className="w-4 h-4" />
            Game Types
          </button>
          <button className={`w-full text-left px-4 py-2 ${display === "games" ? "bg-gray-700" : "hover:bg-gray-700"} rounded-lg flex items-center gap-2`} onClick={() => setDisplay("games")}>
            <Gamepad2 className="w-4 h-4" />
            Games
          </button>
          <button className={`w-full text-left px-4 py-2 ${display === "payments" ? "bg-gray-700" : "hover:bg-gray-700"} rounded-lg flex items-center gap-2`} onClick={() => setDisplay("payments")}>
            <CreditCard className="w-4 h-4" />
            Payments
          </button>
          <button className={`w-full text-left px-4 py-2 ${display === "transactions" ? "bg-gray-700" : "hover:bg-gray-700"} rounded-lg flex items-center gap-2`} onClick={() => setDisplay("transactions")}>
            <ArrowLeftRight className="w-4 h-4" />
            Transactions
          </button>
          <button className={`w-full text-left px-4 py-2 ${display === "players" ? "bg-gray-700" : "hover:bg-gray-700"} rounded-lg flex items-center gap-2`} onClick={() => setDisplay("players")}>
            <Users className="w-4 h-4" />
            Players
          </button>
          <button className={`w-full text-left px-4 py-2 ${display === "bingo-cards" ? "bg-gray-700" : "hover:bg-gray-700"} rounded-lg flex items-center gap-2`} onClick={() => setDisplay("bingo-cards")}>
            <Grid className="w-4 h-4" />
            Bingo Cards
          </button>
          <button className={`w-full text-left px-4 py-2 ${display === "referrals" ? "bg-gray-700" : "hover:bg-gray-700"} rounded-lg flex items-center gap-2`} onClick={() => setDisplay("referrals")}>
            <UserPlus className="w-4 h-4" />
            Referrals
          </button>
          <button className={`w-full text-left px-4 py-2 ${display === "messages" ? "bg-gray-700" : "hover:bg-gray-700"} rounded-lg flex items-center gap-2`} onClick={() => setDisplay("messages")}>
            <MessageSquare className="w-4 h-4" />
            Messages
          </button>
          <button className={`w-full text-left px-4 py-2 ${display === "contact-info" ? "bg-gray-700" : "hover:bg-gray-700"} rounded-lg flex items-center gap-2`} onClick={() => setDisplay("contact-info")}>
            <Phone className="w-4 h-4" />
            Contact Info
          </button>
          <button className={`w-full text-left px-4 py-2 ${display === "logout" ? "bg-gray-700" : "hover:bg-gray-700"} rounded-lg flex items-center gap-2`} onClick={() => setDisplay("logout")}>
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </nav>
      </aside>

      {/* Overlay for mobile */}
      {display === "menu" && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={() => setDisplay("dashboard")}
        />
      )}

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto md:ml-0">
        {display === "dashboard" && <DashboardComponet />}
        {display === "game-types" && <GameTypes />}
        {display === "games" && <Games />}
        {display === "transactions" && <Transactions />}
        {display === "players" && <Players />}
        {display === "bingo-cards" && <BingoCard />}
        {display === "referrals" && <Referrals />}
        {display === "payments" && <Payments />}
        {display === "messages" && <Messages />}
        {display === "contact-info" && <ContactInfo />}
        {display === "logout" && <Logout />}
      </main>
    </div>
  );
}


export default Dashboard;