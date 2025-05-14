import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { accountsApi } from '@/lib/api';
import { DataTable } from '@/components/ui/data-table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Plus, Star, Play, Eye, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { toast } from '@/lib/toast';
import placeholderAvatar from '@/assets/placeholder-avatar.png';

export function Accounts() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [newUsername, setNewUsername] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);

  const { data: accounts, isLoading } = useQuery({
    queryKey: ['accounts'],
    queryFn: () => accountsApi.list({ limit: 100 }),
  });

  const createAccountMutation = useMutation({
    mutationFn: accountsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      setDialogOpen(false);
      setNewUsername('');
      toast.success('Account added successfully');
    },
    onError: (error) => {
      toast.error('Failed to add account');
    },
  });

  const updateAccountMutation = useMutation({
    mutationFn: ({ id, data }) => accountsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });

  const deleteAccountMutation = useMutation({
    mutationFn: accountsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      toast.success('Account deleted successfully');
    },
  });

  const columns = [
    {
      accessorKey: 'username',
      header: 'Username',
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <img
            src={row.original.profile_pic_url || placeholderAvatar}
            alt={row.original.username}
            className="h-8 w-8 rounded-full"
          />
          <span className="font-medium">@{row.original.username}</span>
          {row.original.is_verified && (
            <svg className="h-4 w-4 text-blue-500" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
          )}
        </div>
      ),
    },
    {
      accessorKey: 'full_name',
      header: 'Name',
    },
    {
      accessorKey: 'follower_count',
      header: 'Followers',
      cell: ({ row }) => row.original.follower_count?.toLocaleString() || '-',
    },
    {
      accessorKey: 'following_count',
      header: 'Following',
      cell: ({ row }) => row.original.following_count?.toLocaleString() || '-',
    },
    {
      accessorKey: 'last_scraped',
      header: 'Last Scraped',
      cell: ({ row }) => {
        if (!row.original.last_scraped) return 'Never';
        const date = new Date(row.original.last_scraped);
        return date.toLocaleDateString();
      },
    },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => updateAccountMutation.mutate({
              id: row.original.id,
              data: { is_bookmarked: !row.original.is_bookmarked }
            })}
            title={row.original.is_bookmarked ? 'Remove bookmark' : 'Add bookmark'}
          >
            <Star className={`h-4 w-4 ${row.original.is_bookmarked ? 'fill-yellow-500 text-yellow-500' : ''}`} />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(`/accounts/${row.original.id}/scrape`)}
            title="Run scrape"
          >
            <Play className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(`/accounts/${row.original.id}`)}
            title="View details"
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => {
              if (confirm('Are you sure you want to delete this account?')) {
                deleteAccountMutation.mutate(row.original.id);
              }
            }}
            title="Delete account"
          >
            <Trash2 className="h-4 w-4 text-red-500" />
          </Button>
        </div>
      ),
    },
  ];

  if (isLoading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Accounts</h1>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Account
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Instagram Account</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <Input
                placeholder="Instagram username (without @)"
                value={newUsername}
                onChange={(e) => setNewUsername(e.target.value.replace('@', ''))}
              />
              <Button
                onClick={() => createAccountMutation.mutate({ username: newUsername })}
                disabled={!newUsername || createAccountMutation.isPending}
                className="w-full"
              >
                Add Account
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <DataTable
        columns={columns}
        data={accounts?.data || []}
        searchPlaceholder="Search accounts..."
      />
    </div>
  );
}