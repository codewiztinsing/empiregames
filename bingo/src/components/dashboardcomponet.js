
import { Users, Play, DollarSign, ArrowDown, ArrowUp } from "lucide-react";
import { getDashboardStats, getDashboardRecentStats } from "../services/api";
import { useState, useEffect } from "react";




function DashboardComponet() {
  const [dashboardStats, setDashboardStats] = useState(null);
  const [playersJoinedToday, setPlayersJoinedToday] = useState(null);
  const [totalPlayers, setTotalPlayers] = useState(null);
  const [totalGames, setTotalGames] = useState(null);
  const [revenue, setRevenue] = useState(null);
  const [deposits, setDeposits] = useState(0);
  const [withdrawals, setWithdrawals] = useState(0);
  useEffect(() => {
    getDashboardStats().then(response => {
      console.log("dashboardStats ",response.data);
      setDashboardStats(response.data);
      setPlayersJoinedToday(response.data.playersJoinedToday);
      setTotalPlayers(response.data.totalPlayers);
      setTotalGames(response.data.totalGames);
      setRevenue(response.data.totalBalance);
      setDeposits(response.data.deposits);
      setWithdrawals(response.data.withdrawals);
    });
  }, []);

  if (!dashboardStats) {
    return <div>Loading...</div>;
  }

  const handleTimeRangeChange = (e) => {
    getDashboardRecentStats(e.target.value).then(response => {
      setDashboardStats(response.data);
      setPlayersJoinedToday(response.data.playersJoinedToday || 0);
      setTotalPlayers(response.data.totalPlayers || 0);
      setTotalGames(response.data.totalGames || 0);
      setRevenue(response.data.totalBalance || 0);
      setDeposits(response.data.deposits || 0);
      setWithdrawals(response.data.withdrawals || 0);
    });
  }

  return (

<main className="flex-1 p-6 overflow-y-auto">
<div className="flex justify-between items-center mb-6">
  <h1 className="text-2xl font-bold">Dashboard</h1>
  <div className="flex items-center gap-2">
    <select className="bg-gray-700 p-2 rounded-lg" onChange={handleTimeRangeChange}>
      <option value="last30days">Last 30 days</option>
      <option value="last7days">Last 7 days</option>
      <option value="today">Today</option>
    </select>
    <button className="bg-indigo-600 px-4 py-2 rounded-lg">Refresh</button>
  </div>
</div>

<p className="text-gray-400 mb-6">Showing data for: Last 30 days<br />7/19/2025 to 8/20/2025</p>

{/* Stats Section */}
<div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
  <div className="bg-gray-800 p-6 rounded-xl shadow flex flex-col">
    <div className="flex justify-between items-center">
      <h2 className="text-lg font-semibold">New Users</h2>
      <Users className="text-blue-400" />
    </div>
    <p className="text-2xl font-bold mt-2">{playersJoinedToday}</p>
    <span className="text-gray-400 text-sm">Total Users: {totalPlayers}</span>
  </div>

  <div className="bg-gray-800 p-6 rounded-xl shadow flex flex-col">
    <div className="flex justify-between items-center">
      <h2 className="text-lg font-semibold">Games Played</h2>
      <Play className="text-green-400" />
    </div>
    <p className="text-2xl font-bold mt-2">{totalGames}</p>
    <span className="text-gray-400 text-sm">Total Games: {totalGames}</span>
  </div>

  <div className="bg-gray-800 p-6 rounded-xl shadow flex flex-col">
    <div className="flex justify-between items-center">
      <h2 className="text-lg font-semibold">Revenue</h2>
      <DollarSign className="text-yellow-400" />
    </div>
    <p className="text-2xl font-bold mt-2">{revenue}</p>
    <span className="text-gray-400 text-sm">Total Revenue: {revenue}</span>
  </div>
</div>

{/* Financial Activity */}
<h2 className="text-xl font-bold mb-4">Financial Activity</h2>
<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
  <div className="bg-gray-800 p-6 rounded-xl shadow flex flex-col">
    <div className="flex justify-between items-center">
      <h2 className="text-lg font-semibold">Deposits</h2>
      <ArrowDown className="text-blue-400" />
    </div>
    <p className="text-2xl font-bold mt-2">{deposits}</p>
    <span className="text-gray-400 text-sm">Total Deposits: {deposits}</span>
  </div>

  <div className="bg-gray-800 p-6 rounded-xl shadow flex flex-col">
    <div className="flex justify-between items-center">
      <h2 className="text-lg font-semibold">Withdrawals</h2>
      <ArrowUp className="text-red-400" />
    </div>
    <p className="text-2xl font-bold mt-2">{withdrawals}</p>
    <span className="text-gray-400 text-sm">Total Withdrawals: {withdrawals}</span>
  </div>
</div>
</main>
        
    )
}

export default DashboardComponet;
