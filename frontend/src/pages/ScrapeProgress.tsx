import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { accountsApi, scrapesApi } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle, XCircle, Loader2, RefreshCw, XSquare } from 'lucide-react';
import { CancelScrapeDialog } from '@/components/CancelScrapeDialog';
import { useToast } from '@/components/ui/use-toast';

interface ProgressData {
  status: string;
  message: string;
  progress: number;
  results?: {
    followers_count: number;
    following_count: number;
  };
  retry_after?: number;
  scrape_id?: number;
}

export function ScrapeProgress() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [showCancelDialog, setShowCancelDialog] = useState(false);
  const [canceling, setCanceling] = useState(false);

  const { data: account } = useQuery({
    queryKey: ['account', id],
    queryFn: () => accountsApi.get(Number(id)),
  });

  // Start a new scrape
  const startScrape = async () => {
    try {
      const response = await scrapesApi.create({
        account_id: Number(id),
        scrape_type: 'both',
        use_private_creds: true,
      });
      setJobId(response.data.job_id);
    } catch (error) {
      console.error('Failed to start scrape:', error);
    }
  };

  // Listen to SSE progress updates
  useEffect(() => {
    if (!jobId) {
      startScrape();
      return;
    }

    const eventSource = scrapesApi.progress(jobId);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setProgress(data);
        
        if (data.status === 'completed' || data.status === 'failed') {
          eventSource.close();
        }
      } catch (error) {
        console.error('Error parsing SSE data:', error);
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [jobId]);

  const getStatusIcon = () => {
    if (!progress) return <Loader2 className="h-8 w-8 animate-spin" />;
    
    switch (progress.status) {
      case 'completed':
        return <CheckCircle className="h-8 w-8 text-green-500" />;
      case 'failed':
        return <XCircle className="h-8 w-8 text-red-500" />;
      case 'delayed':
        return <RefreshCw className="h-8 w-8 text-yellow-500 animate-pulse" />;
      default:
        return <Loader2 className="h-8 w-8 animate-spin text-primary" />;
    }
  };

  const getStatusColor = () => {
    if (!progress) return 'text-gray-500';
    
    switch (progress.status) {
      case 'completed':
        return 'text-green-500';
      case 'failed':
        return 'text-red-500';
      case 'delayed':
        return 'text-yellow-500';
      default:
        return 'text-primary';
    }
  };

  const handleCancel = async (savePartial: boolean) => {
    if (!progress?.scrape_id || canceling) return;
    
    setCanceling(true);
    try {
      await scrapesApi.cancel(progress.scrape_id, { save_partial: savePartial });
      toast({
        title: savePartial ? 'Partial results saved' : 'Scrape canceled',
        description: savePartial 
          ? 'The partial results have been saved to your account.' 
          : 'The scrape has been canceled and all data has been discarded.',
      });
      navigate(`/accounts/${id}`);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to cancel the scrape. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setCanceling(false);
      setShowCancelDialog(false);
    }
  };

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Scraping @{account?.data.username}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex flex-col items-center text-center space-y-4">
            {getStatusIcon()}
            <h3 className={`text-lg font-medium ${getStatusColor()}`}>
              {progress?.message || 'Initializing scrape...'}
            </h3>
            
            {progress?.retry_after && (
              <Alert>
                <AlertDescription>
                  Rate limited. Retrying in {progress.retry_after} seconds...
                </AlertDescription>
              </Alert>
            )}
          </div>

          <Progress value={progress?.progress || 0} className="h-3" />
          
          {progress?.results && (
            <div className="grid grid-cols-2 gap-4">
              <Card>
                <CardContent className="p-4">
                  <p className="text-sm font-medium text-muted-foreground">Followers</p>
                  <p className="text-2xl font-bold">{progress.results.followers_count.toLocaleString()}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <p className="text-sm font-medium text-muted-foreground">Following</p>
                  <p className="text-2xl font-bold">{progress.results.following_count.toLocaleString()}</p>
                </CardContent>
              </Card>
            </div>
          )}

          <div className="flex justify-center gap-2">
            {progress?.status === 'completed' && (
              <Button onClick={() => navigate(`/accounts/${id}`)}>
                View Results
              </Button>
            )}
            {progress?.status === 'failed' && (
              <Button onClick={startScrape} variant="outline">
                Try Again
              </Button>
            )}
            {progress?.status !== 'completed' && progress?.status !== 'failed' && progress?.scrape_id && (
              <>
                <Button onClick={() => navigate('/accounts')} variant="outline">
                  Run in Background
                </Button>
                <Button 
                  onClick={() => setShowCancelDialog(true)} 
                  variant="destructive"
                  disabled={canceling}
                >
                  <XSquare className="mr-2 h-4 w-4" />
                  Cancel Scrape
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      <CancelScrapeDialog
        open={showCancelDialog}
        onOpenChange={setShowCancelDialog}
        onCancel={handleCancel}
        scraped={{
          followers: progress?.results?.followers_count || 0,
          following: progress?.results?.following_count || 0,
        }}
      />
    </div>
  );
}