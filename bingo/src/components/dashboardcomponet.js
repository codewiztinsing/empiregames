import { Users, Play, DollarSign, ArrowDown, ArrowUp, Edit, Trash2 } from "lucide-react";

  import { getDashboardStats, getDashboardRecentStats,deleteApiPromotion,createApiPromotion} from "../services/api";
  import { useState, useEffect } from "react";
  import PromotionEditModal from "./promotionEditModal";
  import PromotionAddModal from "./PromotionAddModal";




function DashboardComponet() {
  const [dashboardStats, setDashboardStats] = useState(null);
  const [playersJoinedToday, setPlayersJoinedToday] = useState(null);
  const [totalPlayers, setTotalPlayers] = useState(null);
  const [totalGames, setTotalGames] = useState(null);
  const [revenue, setRevenue] = useState(null);
  const [deposits, setDeposits] = useState(0);
  const [withdrawals, setWithdrawals] = useState(0);
  const [timeRange, setTimeRange] = useState("last 30days");
  const [startDate, setStartDate] = useState(new Date().toLocaleDateString());
  const [endDate, setEndDate] = useState(new Date().toLocaleDateString());
  const [playersJoinedLast30Days, setPlayersJoinedLast30Days] = useState(0);
  const [gamesLast30Days, setGamesLast30Days] = useState(0);
  const [revenueLast30Days, setRevenueLast30Days] = useState(0);
  const [depositsLast30Days, setDepositsLast30Days] = useState(0);
  const [withdrawalsLast30Days, setWithdrawalsLast30Days] = useState(0);
  const [activePromotions, setActivePromotions] = useState([]);
  const [scheduledPromotions, setScheduledPromotions] = useState([]);
  const [inactivePromotions, setInactivePromotions] = useState([]);
  const [allPromotions, setAllPromotions] = useState([]);
  const [quickStats, setQuickStats] = useState({
    activePromotions: 0,
    usersEngaged: 0,
    bonusAwarded: 0,
    conversionRate: 0
  });
  const [editPromotionId, setEditPromotionId] = useState(null);
  const [editPromotionModal, setEditPromotionModal] = useState(false);
  const [addPromotionModal, setAddPromotionModal] = useState(false);
  const handlePromotionSave = (promotion) => {
    console.log("handlePromotionSave ",promotion);
    createApiPromotion(promotion).then(response => {
      console.log("Promotion created successfully:", response.data);
      // Refresh the promotions data
      getDashboardStats().then(refreshResponse => {
        setDashboardStats(refreshResponse.data);
        setActivePromotions(refreshResponse.data.activePromotions);
        setScheduledPromotions(refreshResponse.data.scheduledPromotions);
        setInactivePromotions(refreshResponse.data.inactivePromotions);
        setAllPromotions(refreshResponse.data.allPromotions);
        setQuickStats({
          activePromotions: refreshResponse.data.activePromotions || 0,
          usersEngaged: refreshResponse.data.usersEngaged || 0,
          bonusAwarded: refreshResponse.data.bonusAwarded || 0,
          conversionRate: refreshResponse.data.conversionRate || 0
        });
      });
      // Close the modal
      setAddPromotionModal(false);
    });
  }

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
      setActivePromotions(response.data.activePromotions);
      setScheduledPromotions(response.data.scheduledPromotions);
      setInactivePromotions(response.data.inactivePromotions);
      setAllPromotions(response.data.allPromotions);
      setQuickStats({
        activePromotions: response.data.activePromotions || 0,
        usersEngaged: response.data.usersEngaged || 0,
        bonusAwarded: response.data.bonusAwarded || 0,
        conversionRate: response.data.conversionRate || 0
      });   
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
      setPlayersJoinedLast30Days(response.data.playersJoinedLast30Days || 0);
      setGamesLast30Days(response.data.gamesLast30Days || 0);
      setRevenueLast30Days(response.data.revenueLast30Days || 0);
      setDepositsLast30Days(response.data.depositsLast30Days || 0);
      setWithdrawalsLast30Days(response.data.withdrawalsLast30Days || 0);
      setActivePromotions(response.data.activePromotions || []);
      setScheduledPromotions(response.data.scheduledPromotions || []);
      setInactivePromotions(response.data.inactivePromotions || []);
      setAllPromotions(response.data.allPromotions || []);
      setQuickStats({
        activePromotions: response.data.activePromotions || 0,
        usersEngaged: response.data.usersEngaged || 0,
        bonusAwarded: response.data.bonusAwarded || 0,
        conversionRate: response.data.conversionRate || 0
      });
    });
  }

  const deletePromotion = (id) => {
    deleteApiPromotion(id).then(response => {
      // Show success toast message
      const message = response.data.message || 'Promotion deleted successfully';
      // You would need to implement toast functionality here
      console.log(message);
      
      // Update the state to remove the deleted promotion
      setAllPromotions(prevPromotions => 
        prevPromotions.filter(promotion => promotion.id !== id)
      );
    });
  }

  const editPromotion = (id) => {
    setEditPromotionId(id);
    setEditPromotionModal(true);
    console.log("editPromotion ",id);
  }

  return (
<> 
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

<p className="text-gray-400 mb-6">Showing data for: {timeRange}<br />{startDate} to {endDate}</p>

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

{/* Last 30 Days Summary */}
<h2 className="text-xl font-bold mb-4 mt-8">Last 30 Days Summary</h2>
<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
  <div className="bg-gray-800 p-6 rounded-xl shadow flex flex-col">
    <div className="flex justify-between items-center">
      <h2 className="text-lg font-semibold">New Players</h2>
      <Users className="text-blue-400" />
    </div>
    <p className="text-2xl font-bold mt-2">{playersJoinedLast30Days || 0}</p>
    <span className="text-gray-400 text-sm">Last 30 days</span>
  </div>

  <div className="bg-gray-800 p-6 rounded-xl shadow flex flex-col">
    <div className="flex justify-between items-center">
      <h2 className="text-lg font-semibold">Games Played</h2>
      <Play className="text-green-400" />
    </div>
    <p className="text-2xl font-bold mt-2">{gamesLast30Days || 0}</p>
    <span className="text-gray-400 text-sm">Last 30 days</span>
  </div>

  <div className="bg-gray-800 p-6 rounded-xl shadow flex flex-col">
    <div className="flex justify-between items-center">
      <h2 className="text-lg font-semibold">Revenue</h2>
      <DollarSign className="text-yellow-400" />
    </div>
    <p className="text-2xl font-bold mt-2">{revenueLast30Days || 0}</p>
    <span className="text-gray-400 text-sm">Last 30 days</span>
  </div>
</div>

<div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
  <div className="bg-gray-800 p-6 rounded-xl shadow flex flex-col">
    <div className="flex justify-between items-center">
      <h2 className="text-lg font-semibold">Deposits</h2>
      <ArrowDown className="text-blue-400" />
    </div>
    <p className="text-2xl font-bold mt-2">{depositsLast30Days || 0}</p>
    <span className="text-gray-400 text-sm">Last 30 days</span>
  </div>

  <div className="bg-gray-800 p-6 rounded-xl shadow flex flex-col">
    <div className="flex justify-between items-center">
      <h2 className="text-lg font-semibold">Withdrawals</h2>
      <ArrowUp className="text-red-400" />
    </div>
    <p className="text-2xl font-bold mt-2">{withdrawalsLast30Days || 0}</p>
    <span className="text-gray-400 text-sm">Last 30 days</span>
  </div>
</div>

<h2 className="text-xl font-bold mb-4 mt-8">Promotions Management</h2>
<div className="bg-gray-800 p-6 rounded-xl shadow">
  <div className="flex justify-between items-center mb-6">
    <h3 className="text-lg font-semibold">Active Promotions</h3>
    <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors" onClick={() => setAddPromotionModal(true)}>
      Add New Promotion
    </button>
  </div>
  
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
   
  {
    allPromotions.map((promotion) => (
      <div className="bg-gray-700 p-4 rounded-lg">
      <div className="h-32 bg-gradient-to-r from-orange-500 to-red-500 rounded-lg mb-4 flex items-center justify-center">
        <span className="text-white font-bold text-lg">{promotion.title.length > 20 ? promotion.title.substring(0, 20) + '...' : promotion.title}</span>
      </div>
      <h4 className="font-semibold mb-2">{promotion.title.length > 20 ? promotion.title.substring(0, 20) + '...' : promotion.title}</h4>
      <p className="text-gray-400 text-sm mb-3">{promotion.description.length > 20 ? promotion.description.substring(0, 20) + '...' : promotion.description}</p>
      <div className="flex justify-between items-center text-sm">
        <span className="text-yellow-400">{promotion.status}</span>
        <div className="flex space-x-2">
          <button className="text-blue-400 hover:text-blue-300">
            <Edit size={16}  onClick={() => editPromotion(promotion.id)}/>
          </button>
          <button className="text-red-400 hover:text-red-300">
            <Trash2 size={16}  onClick={() => deletePromotion(promotion.id)}/>
          </button>
        </div>
      </div>
    </div>
    ))
  }
  </div>

  <div className="mt-6 p-4 bg-gray-700 rounded-lg">
    <h4 className="font-semibold mb-3">Quick Stats</h4>
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
      <div>
        <p className="text-2xl font-bold text-blue-400">3</p>
        <p className="text-gray-400 text-sm">Active Promotions</p>
      </div>
      <div>
        <p className="text-2xl font-bold text-green-400">1,247</p>
        <p className="text-gray-400 text-sm">Users Engaged</p>
      </div>
      <div>
        <p className="text-2xl font-bold text-yellow-400">$15,680</p>
        <p className="text-gray-400 text-sm">Bonus Awarded</p>
      </div>
      <div>
        <p className="text-2xl font-bold text-purple-400">24.5%</p>
        <p className="text-gray-400 text-sm">Conversion Rate</p>
      </div>
    </div>
  </div>
</div>


</main>
<PromotionEditModal
  isOpen={editPromotionModal}
  onClose={() => setEditPromotionModal(false)}
  promotionId={editPromotionId}
  promotion={allPromotions.find(promotion => promotion.id === editPromotionId)}
  onSave={handlePromotionSave}
/>
<PromotionAddModal
  isOpen={addPromotionModal}
  onClose={() => setAddPromotionModal(false)}
  onSave={handlePromotionSave}
/>
</>
)
}

export default DashboardComponet;
