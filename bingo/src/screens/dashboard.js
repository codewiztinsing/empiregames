import React, { useState } from "react";
import DashboardComponet from "../components/dashboardcomponet";  
import GameTypes from "../components/GameTypes";
import Games from "../components/Games";
import Transactions from "../components/Transactions";
import Players from "../components/Players";
import Referrals from "../components/Referrals";
import Payments from "../components/Payments";
import Logout from "../components/Logout";
 function Dashboard() {
    const [display, setDisplay] = useState("dashboard");

    
  return (
    <div className="flex w-full h-screen bg-gray-900 text-white">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-800 p-4 flex flex-col">
        <h2 className="text-xl font-bold mb-6">Bingo Admin</h2>
        <nav className="space-y-2">
          <button className="w-full text-left px-4 py-2 bg-gray-700 rounded-lg" onClick={() => setDisplay("dashboard")}>Dashboard</button>
          <button className="w-full text-left px-4 py-2 hover:bg-gray-700 rounded-lg" onClick={() => setDisplay("game-types")}>Game Types</button>
          <button className="w-full text-left px-4 py-2 hover:bg-gray-700 rounded-lg" onClick={() => setDisplay("games")}>Games</button>
          <button className="w-full text-left px-4 py-2 hover:bg-gray-700 rounded-lg" onClick={() => setDisplay("payments")}>Payments</button>
          <button className="w-full text-left px-4 py-2 hover:bg-gray-700 rounded-lg" onClick={() => setDisplay("transactions")}>Transactions</button>
          <button className="w-full text-left px-4 py-2 hover:bg-gray-700 rounded-lg" onClick={() => setDisplay("players")}>Players</button>
          <button className="w-full text-left px-4 py-2 hover:bg-gray-700 rounded-lg" onClick={() => setDisplay("bingo-cards")}>Bingo Cards</button>
          <button className="w-full text-left px-4 py-2 hover:bg-gray-700 rounded-lg" onClick={() => setDisplay("referrals")}>Referrals</button>
          <button className="w-full text-left px-4 py-2 hover:bg-gray-700 rounded-lg" onClick={() => setDisplay("logout")}>Logout</button>
        </nav>
      </aside>

      {/* Main Dashboard */}
      {display === "dashboard" && <DashboardComponet />}
      {display === "game-types" && <GameTypes />}
      {display === "games" && <Games />}
      {display === "transactions" && <Transactions />}
      {display === "players" && <Players />}
      {display === "referrals" && <Referrals />}
      {display === "payments" && <Payments />}
      {display === "logout" && <Logout />}
    </div>
  );
}


export default Dashboard;