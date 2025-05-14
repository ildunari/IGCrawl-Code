import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { accountsApi, scrapesApi, exportApi } from '@/lib/api';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { DataTable } from '@/components/ui/data-table';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Download, ExternalLink, RefreshCw, Users, UserMinus, UserPlus } from 'lucide-react';
import { toast } from '@/lib/toast';

export function Followers() {
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState('followers');
  const [exporting, setExporting] = useState(false);

  const { data: account, isLoading: accountLoading } = useQuery({
    queryKey: ['account', id],
    queryFn: () => accountsApi.get(Number(id)),
  });

  const { data: latestScrape } = useQuery({
    queryKey: ['latest-scrape', id],
    queryFn: async () => {
      const scrapes = await scrapesApi.getByAccount(Number(id), { limit: 1 });
      return scrapes.data[0];
    },
  });

  const { data: followers, isLoading: followersLoading } = useQuery({
    queryKey: ['followers', id, activeTab],
    queryFn: async () => {
      if (!latestScrape) return [];
      const response = await exportApi.followers(Number(id), {
        format: 'json',
        filter_type: activeTab === 'mutuals' ? 'mutuals' : activeTab,
      });
      return response.data;
    },
    enabled: !!latestScrape,
  });

  const handleExport = async (format: 'csv' | 'xlsx') => {
    try {
      setExporting(true);
      const response = await exportApi.followers(Number(id), {
        format,
        filter_type: activeTab === 'mutuals' ? 'mutuals' : activeTab,
      });
      
      // Create download link
      const blob = new Blob([response.data], { 
        type: format === 'csv' ? 'text/csv' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${account.data.username}_${activeTab}_${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success(`Exported as ${format.toUpperCase()}`);
    } catch (error) {
      toast.error('Export failed');
    } finally {
      setExporting(false);
    }
  };

  const columns = [
    {
      accessorKey: 'username',
      header: 'Username',
      cell: ({ row }) => (
        <div className="flex items-center gap-3">
          <Avatar className="h-8 w-8">
            <AvatarImage src={row.original.profile_pic_url} />
            <AvatarFallback>{row.original.username[0].toUpperCase()}</AvatarFallback>
          </Avatar>
          <div className="flex items-center gap-2">
            <a 
              href={`https://instagram.com/${row.original.username}`}
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium hover:underline flex items-center gap-1"
            >
              @{row.original.username}
              <ExternalLink className="h-3 w-3" />
            </a>
            {row.original.is_verified && (
              <svg className="h-4 w-4 text-blue-500" viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
            )}
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'full_name',
      header: 'Name',
    },
    {
      accessorKey: 'relation_type',
      header: 'Type',
      cell: ({ row }) => (
        <Badge variant={row.original.relation_type === 'follower' ? 'default' : 'secondary'}>
          {row.original.relation_type}
        </Badge>
      ),
    },
    {
      accessorKey: 'is_mutual',
      header: 'Mutual',
      cell: ({ row }) => (
        row.original.is_mutual ? (
          <Badge variant="outline" className="bg-green-50 text-green-700">Yes</Badge>
        ) : (
          <Badge variant="outline">No</Badge>
        )
      ),
    },
    {
      accessorKey: 'is_private',
      header: 'Private',
      cell: ({ row }) => (
        row.original.is_private ? (
          <Badge variant="outline" className="bg-gray-50">Private</Badge>
        ) : null
      ),
    },
    {
      accessorKey: 'first_seen',
      header: 'First Seen',
      cell: ({ row }) => new Date(row.original.first_seen).toLocaleDateString(),
    },
  ];

  if (accountLoading) {
    return <div className="p-8">Loading...</div>;
  }

  const accountData = account?.data;

  return (
    <div className="p-8">
      {/* Account Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <Avatar className="h-16 w-16">
              <AvatarImage src={accountData?.profile_pic_url} />
              <AvatarFallback>{accountData?.username[0].toUpperCase()}</AvatarFallback>
            </Avatar>
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2">
                @{accountData?.username}
                {accountData?.is_verified && (
                  <svg className="h-6 w-6 text-blue-500" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                  </svg>
                )}
              </h1>
              <p className="text-muted-foreground">{accountData?.full_name}</p>
            </div>
          </div>
          <Button variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Run New Scrape
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Followers</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{accountData?.follower_count?.toLocaleString() || 0}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Following</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{accountData?.following_count?.toLocaleString() || 0}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">New Followers</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                +{latestScrape?.new_followers || 0}
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Lost Followers</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                -{latestScrape?.lost_followers || 0}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Followers Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <div className="flex justify-between items-center mb-4">
          <TabsList>
            <TabsTrigger value="followers" className="gap-2">
              <Users className="h-4 w-4" />
              Followers
            </TabsTrigger>
            <TabsTrigger value="following" className="gap-2">
              <UserPlus className="h-4 w-4" />
              Following
            </TabsTrigger>
            <TabsTrigger value="mutuals" className="gap-2">
              <UserMinus className="h-4 w-4" />
              Mutuals
            </TabsTrigger>
          </TabsList>
          
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleExport('csv')}
              disabled={exporting || !followers?.data}
            >
              <Download className="h-4 w-4 mr-1" />
              CSV
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleExport('xlsx')}
              disabled={exporting || !followers?.data}
            >
              <Download className="h-4 w-4 mr-1" />
              Excel
            </Button>
          </div>
        </div>

        <TabsContent value={activeTab}>
          <DataTable
            columns={columns}
            data={followers?.data || []}
            searchPlaceholder={`Search ${activeTab}...`}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}