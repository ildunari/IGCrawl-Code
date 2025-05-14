import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Save, Key, Shield, Server, Archive } from 'lucide-react';
import { toast } from '@/lib/toast';

export function Settings() {
  const [settings, setSettings] = useState({
    instagramUsername: '',
    instagramPassword: '',
    encryptionKey: '',
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

  const handleSave = async () => {
    try {
      setSaving(true);
      // TODO: Implement settings save API call
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      toast.success('Settings saved successfully');
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  return (
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
            Configure credentials for accessing private accounts. Leave blank to only scrape public accounts.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="username">Username</Label>
            <Input
              id="username"
              type="text"
              value={settings.instagramUsername}
              onChange={(e) => setSettings({ ...settings, instagramUsername: e.target.value })}
              placeholder="Instagram username"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type={showPasswords ? "text" : "password"}
              value={settings.instagramPassword}
              onChange={(e) => setSettings({ ...settings, instagramPassword: e.target.value })}
              placeholder="Instagram password"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="encryption-key">Encryption Key</Label>
            <Input
              id="encryption-key"
              type={showPasswords ? "text" : "password"}
              value={settings.encryptionKey}
              onChange={(e) => setSettings({ ...settings, encryptionKey: e.target.value })}
              placeholder="AES-256 encryption key"
            />
            <p className="text-sm text-muted-foreground">
              This key is used to encrypt your credentials. Keep it safe!
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Switch
              checked={showPasswords}
              onCheckedChange={setShowPasswords}
            />
            <Label>Show passwords</Label>
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
          <div className="space-y-2">
            <Label htmlFor="proxy">Proxy URL</Label>
            <Input
              id="proxy"
              type="text"
              value={settings.proxyUrl}
              onChange={(e) => setSettings({ ...settings, proxyUrl: e.target.value })}
              placeholder="http://proxy.example.com:8080"
            />
          </div>
        </CardContent>
      </Card>

      {/* Rate Limiting */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Rate Limiting
          </CardTitle>
          <CardDescription>
            Configure rate limiting based on Instagram's actual limits. Default settings are safe for 24/7 operation.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            <Alert>
              <AlertDescription>
                Instagram allows ~200 requests/hour. Our safe default (2/min = 120/hour) stays well under this limit.
              </AlertDescription>
            </Alert>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="rate-limit">Requests per minute</Label>
                <Input
                  id="rate-limit"
                  type="number"
                  value={settings.rateLimitPerMinute}
                  onChange={(e) => setSettings({ ...settings, rateLimitPerMinute: parseInt(e.target.value) })}
                />
                <p className="text-sm text-muted-foreground">
                  Safe: 2, Moderate: 3, Risky: 4+
                </p>
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
                  Time between requests (before jitter)
                </p>
              </div>
            </div>
            <Separator />
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="jitter-min">Minimum jitter (seconds)</Label>
                <Input
                  id="jitter-min"
                  type="number"
                  value={settings.jitterSecondsMin}
                  onChange={(e) => setSettings({ ...settings, jitterSecondsMin: parseInt(e.target.value) })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="jitter-max">Maximum jitter (seconds)</Label>
                <Input
                  id="jitter-max"
                  type="number"
                  value={settings.jitterSecondsMax}
                  onChange={(e) => setSettings({ ...settings, jitterSecondsMax: parseInt(e.target.value) })}
                />
              </div>
            </div>
            <p className="text-sm text-muted-foreground">
              Random delay added to avoid detection patterns
            </p>
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
              <Label>Enable daily scrapes</Label>
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
        <Button onClick={handleSave} disabled={saving} className="w-full sm:w-auto">
          <Save className="h-4 w-4 mr-2" />
          {saving ? 'Saving...' : 'Save Settings'}
        </Button>
      </div>
    </div>
  );
}