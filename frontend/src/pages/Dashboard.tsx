import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { accountsApi, scrapesApi } from '@/lib/api';
import { Users, Database, Activity, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function Dashboard() {
  const { data: accounts, isLoading: accountsLoading } = useQuery({
    queryKey: ['accounts'],
    queryFn: () => accountsApi.list({ limit: 100 }),
  });

  const { data: recentScrapes, isLoading: scrapesLoading } = useQuery({
    queryKey: ['recent-scrapes'],
    queryFn: async () => {
      // Get all scrapes sorted by date
      const scrapes = [];
      if (accounts?.data) {
        for (const account of accounts.data) {
          const response = await scrapesApi.getByAccount(account.id, { limit: 10 });
          scrapes.push(...response.data);
        }
      }
      return scrapes.sort((a, b) => new Date(b.completed_at).getTime() - new Date(a.completed_at).getTime()).slice(0, 10);
    },
    enabled: !!accounts?.data,
  });

  const stats = React.useMemo(() => {
    if (!accounts?.data) return null;
    
    const totalAccounts = accounts.data.length;
    const totalFollowers = accounts.data.reduce((sum, acc) => sum + (acc.follower_count || 0), 0);
    const bookmarkedAccounts = accounts.data.filter(acc => acc.is_bookmarked).length;
    const recentlyScraped = accounts.data.filter(acc => {
      if (!acc.last_scraped) return false;
      const dayAgo = new Date();
      dayAgo.setDate(dayAgo.getDate() - 1);
      return new Date(acc.last_scraped) > dayAgo;
    }).length;

    return {
      totalAccounts,
      totalFollowers,
      bookmarkedAccounts,
      recentlyScraped,
    };
  }, [accounts]);

  const chartData = React.useMemo(() => {
    if (!recentScrapes) return [];
    
    // Group scrapes by date and calculate totals
    const dataByDate = {};
    recentScrapes.forEach(scrape => {
      if (scrape.completed_at && scrape.followers_count) {
        const date = new Date(scrape.completed_at).toLocaleDateString();
        if (!dataByDate[date]) {
          dataByDate[date] = {
            date,
            followers: 0,
            following: 0,
          };
        }
        dataByDate[date].followers = Math.max(dataByDate[date].followers, scrape.followers_count);
        dataByDate[date].following = Math.max(dataByDate[date].following, scrape.following_count || 0);
      }
    });
    
    return Object.values(dataByDate).sort((a, b) => new Date(a.date) - new Date(b.date));
  }, [recentScrapes]);

  if (accountsLoading || scrapesLoading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      
      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Accounts</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalAccounts || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Followers</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalFollowers?.toLocaleString() || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Bookmarked</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.bookmarkedAccounts || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recently Scraped</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.recentlyScraped || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Growth Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Growth Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="followers" stroke="#E1306C" name="Followers" />
                <Line type="monotone" dataKey="following" stroke="#8884d8" name="Following" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}