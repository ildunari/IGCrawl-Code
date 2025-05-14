import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  Database, 
  Settings,
  Moon,
  Sun,
  Menu,
  X
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface SidebarProps {
  darkMode: boolean;
  setDarkMode: (value: boolean) => void;
}

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/accounts', icon: Users, label: 'Accounts' },
  { path: '/scrapes', icon: Database, label: 'Scrapes' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export function Sidebar({ darkMode, setDarkMode }: SidebarProps) {
  const location = useLocation();
  const [collapsed, setCollapsed] = React.useState(false);

  return (
    <div className={cn(
      "relative h-screen bg-card border-r transition-all duration-300",
      collapsed ? "w-16" : "w-64"
    )}>
      {/* Logo and collapse button */}
      <div className="flex items-center justify-between p-4 border-b">
        {!collapsed && (
          <h1 className="text-xl font-bold text-primary">IGCrawl</h1>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed(!collapsed)}
          className="h-8 w-8"
        >
          {collapsed ? <Menu className="h-4 w-4" /> : <X className="h-4 w-4" />}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg transition-colors",
                "hover:bg-accent hover:text-accent-foreground",
                isActive && "bg-primary text-primary-foreground",
                collapsed && "justify-center"
              )}
              title={collapsed ? item.label : undefined}
            >
              <Icon className="h-5 w-5 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Theme toggle */}
      <div className="absolute bottom-4 left-4 right-4">
        <Button
          variant="outline"
          size={collapsed ? "icon" : "default"}
          onClick={() => setDarkMode(!darkMode)}
          className={cn("w-full", collapsed && "w-8")}
          title={collapsed ? "Toggle theme" : undefined}
        >
          {darkMode ? (
            <>
              <Sun className="h-4 w-4" />
              {!collapsed && <span className="ml-2">Light Mode</span>}
            </>
          ) : (
            <>
              <Moon className="h-4 w-4" />
              {!collapsed && <span className="ml-2">Dark Mode</span>}
            </>
          )}
        </Button>
      </div>
    </div>
  );
}