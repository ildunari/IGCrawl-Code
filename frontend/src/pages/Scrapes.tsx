import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { scrapesApi, accountsApi } from '@/lib/api';
import { DataTable } from '@/components/ui/data-table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { format, formatDistanceToNow } from 'date-fns';
import { Play, Eye, Clock, CheckCircle, XCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function Scrapes() {
  const navigate = useNavigate();

  // Get all accounts to fetch their scrapes
  const { data: accounts } = useQuery({
    queryKey: ['accounts'],
    queryFn: () => accountsApi.list({ limit: 100 }),
  });

  // Get all scrapes
  const { data: scrapes, isLoading } = useQuery({
    queryKey: ['all-scrapes'],
    queryFn: async () => {
      if (!accounts?.data) return [];
      
      const allScrapes = [];
      for (const account of accounts.data) {
        const response = await scrapesApi.getByAccount(account.id, { limit: 20 });
        allScrapes.push(...response.data.map(scrape => ({ 
          ...scrape, 
          account_username: account.username,
          account_id: account.id 
        })));
      }
      
      // Sort by date descending
      return allScrapes.sort((a, b) => {
        const dateA = new Date(a.started_at || a.created_at);
        const dateB = new Date(b.started_at || b.created_at);
        return dateB.getTime() - dateA.getTime();
      });
    },
    enabled: !!accounts?.data,
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge className="bg-green-500">Completed</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
      case 'in_progress':
        return <Badge className="bg-blue-500">In Progress</Badge>;
      default:
        return <Badge variant="secondary">Pending</Badge>;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'in_progress':
        return <Clock className="h-4 w-4 text-blue-500 animate-pulse" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const columns = [
    {
      accessorKey: 'account_username',
      header: 'Account',
      cell: ({ row }) => (
        <div className="font-medium">@{row.original.account_username}</div>
      ),
    },
    {
      accessorKey: 'scrape_type',
      header: 'Type',
      cell: ({ row }) => (
        <Badge variant="outline">{row.original.scrape_type}</Badge>
      ),
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          {getStatusIcon(row.original.status)}
          {getStatusBadge(row.original.status)}
        </div>
      ),
    },
    {
      accessorKey: 'followers_count',
      header: 'Followers',
      cell: ({ row }) => row.original.followers_count?.toLocaleString() || '-',
    },
    {
      accessorKey: 'following_count',
      header: 'Following',
      cell: ({ row }) => row.original.following_count?.toLocaleString() || '-',
    },
    {
      accessorKey: 'started_at',
      header: 'Started',
      cell: ({ row }) => {
        if (!row.original.started_at) return '-';
        const date = new Date(row.original.started_at);
        return (
          <div className="text-sm">
            <div>{format(date, 'MMM d, yyyy')}</div>
            <div className="text-muted-foreground">
              {formatDistanceToNow(date, { addSuffix: true })}
            </div>
          </div>
        );
      },
    },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          {row.original.status === 'in_progress' && row.original.job_id && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate(`/accounts/${row.original.account_id}/scrape`)}
              title="View progress"
            >
              <Eye className="h-4 w-4" />
            </Button>
          )}
          {row.original.status === 'completed' && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate(`/accounts/${row.original.account_id}`)}
              title="View results"
            >
              <Eye className="h-4 w-4" />
            </Button>
          )}
          {(row.original.status === 'failed' || row.original.status === 'pending') && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate(`/accounts/${row.original.account_id}/scrape`)}
              title="Retry scrape"
            >
              <Play className="h-4 w-4" />
            </Button>
          )}
        </div>
      ),
    },
  ];

  // Calculate stats
  const stats = React.useMemo(() => {
    if (!scrapes) return null;
    
    const completed = scrapes.filter(s => s.status === 'completed').length;
    const failed = scrapes.filter(s => s.status === 'failed').length;
    const inProgress = scrapes.filter(s => s.status === 'in_progress').length;
    const totalFollowers = scrapes.reduce((sum, s) => sum + (s.followers_count || 0), 0);
    
    return {
      total: scrapes.length,
      completed,
      failed,
      inProgress,
      totalFollowers,
    };
  }, [scrapes]);

  if (isLoading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Scrapes</h1>
      
      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4 mb-8">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Scrapes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.completed || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Failed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats?.failed || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Followers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalFollowers?.toLocaleString() || 0}</div>
          </CardContent>
        </Card>
      </div>

      <DataTable
        columns={columns}
        data={scrapes || []}
        searchPlaceholder="Search scrapes..."
      />
    </div>
  );
}