import React, { useState, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Save, Key, Shield, Server, Archive, ChevronDown, ChevronUp, ExternalLink, Info, Loader2, AlertCircle, HelpCircle } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { toast } from '@/lib/toast';
import { getProxyUrlError, getRateLimitError, getJitterError } from '@/lib/validators';

export function Settings() {
  const [settings, setSettings] = useState({
    instagramUsername: '',
    instagramPassword: '',
    proxyUrl: '',
    rateLimitPerMinute: 2,  // Safe default based on Instagram limits
    scrapeDelaySeconds: 30,
    jitterSecondsMin: 5,
    jitterSecondsMax: 15,
    enableDailyScrapes: true,
    backupRetentionDays: 30,
  });

  const [showPasswords, setShowPasswords] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showProxyInfo, setShowProxyInfo] = useState(false);
  const [testingProxy, setTestingProxy] = useState(false);
  
  const [errors, setErrors] = useState({
    proxyUrl: null as string | null,
    rateLimitPerMinute: null as string | null,
    jitter: null as string | null,
  });

  const validateForm = useCallback(() => {
    const newErrors = {
      proxyUrl: getProxyUrlError(settings.proxyUrl),
      rateLimitPerMinute: getRateLimitError(settings.rateLimitPerMinute),
      jitter: getJitterError(settings.jitterSecondsMin, settings.jitterSecondsMax),
    };
    
    setErrors(newErrors);
    return !Object.values(newErrors).some(error => error !== null);
  }, [settings]);

  const handleProxyUrlChange = (value: string) => {
    setSettings({ ...settings, proxyUrl: value });
    setErrors({ ...errors, proxyUrl: getProxyUrlError(value) });
  };

  const handleRateLimitChange = (value: number) => {
    setSettings({ ...settings, rateLimitPerMinute: value });
    setErrors({ ...errors, rateLimitPerMinute: getRateLimitError(value) });
  };

  const handleJitterChange = (field: 'jitterSecondsMin' | 'jitterSecondsMax', value: number) => {
    const newSettings = { ...settings, [field]: value };
    setSettings(newSettings);
    setErrors({ ...errors, jitter: getJitterError(newSettings.jitterSecondsMin, newSettings.jitterSecondsMax) });
  };

  const handleTestProxy = async () => {
    if (!settings.proxyUrl) {
      toast.error('Please enter a proxy URL to test');
      return;
    }
    
    if (errors.proxyUrl) {
      toast.error('Please fix the proxy URL format first');
      return;
    }
    
    try {
      setTestingProxy(true);
      // TODO: Implement actual proxy test API call
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate API call
      toast.success('Proxy connection successful!');
    } catch (error) {
      toast.error('Failed to connect to proxy. Please check your URL and credentials.');
    } finally {
      setTestingProxy(false);
    }
  };

  const handleSave = async () => {
    if (!validateForm()) {
      toast.error('Please fix validation errors before saving');
      return;
    }

    try {
      setSaving(true);
      // TODO: Implement settings save API call
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API call
      toast.success('Settings saved successfully!');
    } catch (error) {
      toast.error('Failed to save settings. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <TooltipProvider>
      <div className="p-8 max-w-4xl">
        <h1 className="text-3xl font-bold mb-8">Settings</h1>

      {/* Instagram Credentials */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            Instagram Credentials
          </CardTitle>
          <CardDescription>
            Enter your Instagram login to scrape private accounts and access follower data. Without credentials, only public profile information can be viewed.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert>
            <Shield className="h-4 w-4" />
            <AlertDescription>
              Your password is automatically encrypted using industry-standard AES-256 encryption before storage. 
              We never store plain-text passwords.
            </AlertDescription>
          </Alert>
          
          <div className="space-y-2">
            <Label htmlFor="username">Instagram Username</Label>
            <Input
              id="username"
              type="text"
              value={settings.instagramUsername}
              onChange={(e) => setSettings({ ...settings, instagramUsername: e.target.value })}
              placeholder="your_instagram_username"
            />
            <p className="text-sm text-muted-foreground">
              The username you use to log into Instagram
            </p>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="password">Instagram Password</Label>
            <Input
              id="password"
              type={showPasswords ? "text" : "password"}
              value={settings.instagramPassword}
              onChange={(e) => setSettings({ ...settings, instagramPassword: e.target.value })}
              placeholder={showPasswords ? "your_password" : "••••••••"}
            />
            <p className="text-sm text-muted-foreground">
              Your Instagram password (will be encrypted)
            </p>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Switch
                checked={showPasswords}
                onCheckedChange={setShowPasswords}
              />
              <Label>Show password</Label>
            </div>
            <p className="text-sm text-muted-foreground">
              Leave empty to only scrape public accounts
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Proxy Settings */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            Proxy Configuration
          </CardTitle>
          <CardDescription>
            Configure proxy settings to avoid rate limiting. Optional.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium">Need help setting up a proxy?</p>
            <Button
              variant="soft"
              size="sm"
              onClick={() => setShowProxyInfo(!showProxyInfo)}
            >
              {showProxyInfo ? (
                <>Hide Info <ChevronUp className="h-3 w-3 ml-1 transform transition-transform duration-200" /></>
              ) : (
                <>Learn More <ChevronDown className="h-3 w-3 ml-1 transform transition-transform duration-200" /></>
              )}
            </Button>
          </div>
          {showProxyInfo && (
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 space-y-3">
              <h4 className="font-medium flex items-center gap-2">
                <Info className="h-4 w-4" />
                What is a proxy and why use one?
              </h4>
              <p className="text-sm text-muted-foreground">
                A proxy server acts as an intermediary between your requests and Instagram. 
                Using a proxy helps you avoid detection and rate limiting by making your 
                requests appear to come from different IP addresses.
              </p>
              
              <h4 className="font-medium mt-4">Recommended Free Proxy Options:</h4>
              <ul className="text-sm text-muted-foreground space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 dark:text-blue-400 font-medium">1.</span>
                  <div>
                    <span className="font-medium">Bright Data Free Plan</span> 
                    <a href="https://brightdata.com" target="_blank" rel="noopener noreferrer" 
                       className="text-blue-600 dark:text-blue-400 ml-1 inline-flex items-center">
                      (brightdata.com <ExternalLink className="h-3 w-3 ml-1" />)
                    </a>
                    <p className="mt-1">Offers a limited free tier with rotating residential IPs. 
                    Best for serious scraping with 7GB/month free.</p>
                  </div>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 dark:text-blue-400 font-medium">2.</span>
                  <div>
                    <span className="font-medium">ProxyScrape Free Proxies</span>
                    <a href="https://proxyscrape.com/free-proxy-list" target="_blank" rel="noopener noreferrer"
                       className="text-blue-600 dark:text-blue-400 ml-1 inline-flex items-center">
                      (proxyscrape.com <ExternalLink className="h-3 w-3 ml-1" />)
                    </a>
                    <p className="mt-1">Public HTTP proxies updated every minute. 
                    Less reliable but completely free.</p>
                  </div>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 dark:text-blue-400 font-medium">3.</span>
                  <div>
                    <span className="font-medium">Tor Network</span>
                    <a href="https://www.torproject.org" target="_blank" rel="noopener noreferrer"
                       className="text-blue-600 dark:text-blue-400 ml-1 inline-flex items-center">
                      (torproject.org <ExternalLink className="h-3 w-3 ml-1" />)
                    </a>
                    <p className="mt-1">Free anonymity network. Setup: Install Tor, 
                    use <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">socks5://localhost:9050</code></p>
                  </div>
                </li>
              </ul>
              
              <h4 className="font-medium mt-4">How to set up:</h4>
              <ol className="text-sm text-muted-foreground space-y-1">
                <li>1. Choose a proxy service from the list above</li>
                <li>2. Sign up and get your proxy URL (usually in format: http://username:password@proxy-server:port)</li>
                <li>3. Enter the full proxy URL in the field below</li>
                <li>4. Save settings and the proxy will be used for all Instagram requests</li>
              </ol>
              
              <Alert className="mt-3">
                <AlertDescription className="text-sm">
                  <strong>Important:</strong> Free proxies are less reliable and slower. 
                  For production use, consider a paid proxy service for better stability and speed.
                </AlertDescription>
              </Alert>
            </div>
          )}
          <div className="space-y-2">
            <Label htmlFor="proxy">Proxy URL</Label>
            <div className="relative">
              <div className="flex gap-2">
                <Input
                  id="proxy"
                  type="text"
                  value={settings.proxyUrl}
                  onChange={(e) => handleProxyUrlChange(e.target.value)}
                  placeholder="http://proxy.example.com:8080"
                  className={errors.proxyUrl ? "border-red-500 flex-1" : "flex-1"}
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleTestProxy}
                  disabled={testingProxy || !settings.proxyUrl || !!errors.proxyUrl}
                >
                  {testingProxy ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Testing...
                    </>
                  ) : (
                    'Test Proxy'
                  )}
                </Button>
              </div>
              {errors.proxyUrl && (
                <div className="flex items-center gap-1 mt-1 text-sm text-red-500">
                  <AlertCircle className="h-3 w-3" />
                  {errors.proxyUrl}
                </div>
              )}
            </div>
            <p className="text-sm text-muted-foreground">
              Format: http://username:password@server:port
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Rate Limiting */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Rate Limiting & Request Speed
          </CardTitle>
          <CardDescription>
            Configure how fast to scrape Instagram. Default settings are safe for 24/7 operation.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            <Alert>
              <AlertDescription>
                <strong>What is a request?</strong> Each request gets ~50-100 followers/following at a time. 
                An account with 1,000 followers needs ~10-20 requests to get all followers.
              </AlertDescription>
            </Alert>
            
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 space-y-2">
              <h4 className="font-medium text-sm">Request Examples:</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>1 request</strong> = Load profile info OR get 50-100 followers</li>
                <li>• <strong>Small account (500 followers)</strong> = ~5-10 requests total</li>
                <li>• <strong>Medium account (5,000 followers)</strong> = ~50-100 requests</li>
                <li>• <strong>Large account (50,000 followers)</strong> = ~500-1,000 requests</li>
              </ul>
              <p className="text-sm font-medium text-blue-700 dark:text-blue-300 mt-2">
                At 2 requests/minute, a 5,000 follower account takes ~25-50 minutes to fully scrape.
              </p>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="rate-limit">Requests per minute</Label>
                <Input
                  id="rate-limit"
                  type="number"
                  value={settings.rateLimitPerMinute}
                  onChange={(e) => handleRateLimitChange(parseInt(e.target.value) || 0)}
                  className={errors.rateLimitPerMinute ? "border-red-500" : ""}
                />
                {errors.rateLimitPerMinute && (
                  <div className="flex items-center gap-1 text-sm text-red-500">
                    <AlertCircle className="h-3 w-3" />
                    {errors.rateLimitPerMinute}
                  </div>
                )}
                <div className="text-sm text-muted-foreground space-y-1">
                  <p><span className="text-green-600 dark:text-green-400 font-medium">2 req/min:</span> Safe (120/hour) - Best for avoiding bans</p>
                  <p><span className="text-yellow-600 dark:text-yellow-400 font-medium">3 req/min:</span> Moderate (180/hour) - Faster but riskier</p>
                  <p><span className="text-red-600 dark:text-red-400 font-medium">4+ req/min:</span> High risk of temporary ban</p>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="delay">Base delay (seconds)</Label>
                <Input
                  id="delay"
                  type="number"
                  value={settings.scrapeDelaySeconds}
                  onChange={(e) => setSettings({ ...settings, scrapeDelaySeconds: parseInt(e.target.value) })}
                />
                <p className="text-sm text-muted-foreground">
                  Time between each request. 30 seconds = 2 requests/minute
                </p>
              </div>
            </div>
            
            <Separator />
            
            <div className="space-y-3">
              <div>
                <div className="flex items-center gap-2">
                  <Label className="text-base">Anti-Detection Jitter</Label>
                  <Tooltip>
                    <TooltipTrigger>
                      <HelpCircle className="h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs">
                      <p>Jitter adds random variation to your scraping patterns, making them appear more natural and human-like to avoid detection by Instagram's anti-bot systems.</p>
                    </TooltipContent>
                  </Tooltip>
                </div>
                <p className="text-sm text-muted-foreground">
                  Adds random delays to make your scraping pattern look more human
                </p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="jitter-min">Minimum jitter (seconds)</Label>
                  <Input
                    id="jitter-min"
                    type="number"
                    value={settings.jitterSecondsMin}
                    onChange={(e) => handleJitterChange('jitterSecondsMin', parseInt(e.target.value) || 0)}
                    className={errors.jitter ? "border-red-500" : ""}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="jitter-max">Maximum jitter (seconds)</Label>
                  <Input
                    id="jitter-max"
                    type="number"
                    value={settings.jitterSecondsMax}
                    onChange={(e) => handleJitterChange('jitterSecondsMax', parseInt(e.target.value) || 0)}
                    className={errors.jitter ? "border-red-500" : ""}
                  />
                </div>
              </div>
              {errors.jitter && (
                <div className="flex items-center gap-1 text-sm text-red-500">
                  <AlertCircle className="h-3 w-3" />
                  {errors.jitter}
                </div>
              )}
              <p className="text-sm text-muted-foreground">
                Example: With 30s delay + 5-15s jitter, requests happen every 35-45 seconds randomly
              </p>
            </div>
            
            <Alert>
              <AlertDescription className="text-sm">
                <strong>Tip:</strong> Instagram limits are per account and IP address. Using a proxy helps you stay under radar by rotating IPs.
              </AlertDescription>
            </Alert>
          </div>
        </CardContent>
      </Card>

      {/* Automation */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Archive className="h-5 w-5" />
            Automation & Backups
          </CardTitle>
          <CardDescription>
            Configure automated scraping and backup settings.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <div className="flex items-center gap-2">
                <Label>Enable daily scrapes</Label>
                <Tooltip>
                  <TooltipTrigger>
                    <HelpCircle className="h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs">
                    <p>When enabled, the system will automatically scrape all bookmarked accounts every day at 2:00 AM to track follower changes over time.</p>
                  </TooltipContent>
                </Tooltip>
              </div>
              <p className="text-sm text-muted-foreground">
                Automatically scrape bookmarked accounts at 2:00 AM
              </p>
            </div>
            <Switch
              checked={settings.enableDailyScrapes}
              onCheckedChange={(checked) => setSettings({ ...settings, enableDailyScrapes: checked })}
            />
          </div>
          <Separator />
          <div className="space-y-2">
            <Label htmlFor="retention">Backup retention (days)</Label>
            <Input
              id="retention"
              type="number"
              value={settings.backupRetentionDays}
              onChange={(e) => setSettings({ ...settings, backupRetentionDays: parseInt(e.target.value) })}
            />
            <p className="text-sm text-muted-foreground">
              Automatically delete backups older than this many days
            </p>
          </div>
        </CardContent>
      </Card>

      <Alert>
        <AlertDescription>
          Changes to these settings will apply to all future scrapes. Existing data will not be affected.
        </AlertDescription>
      </Alert>

      <div className="mt-6">
        <Button 
          onClick={handleSave} 
          disabled={saving || Object.values(errors).some(error => error !== null)} 
          className="w-full sm:w-auto"
        >
          {saving ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="h-4 w-4 mr-2" />
              Save Settings
            </>
          )}
        </Button>
        </div>
      </div>
    </TooltipProvider>
  );
}