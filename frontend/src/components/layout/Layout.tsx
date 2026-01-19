import { Link, Outlet, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Settings,
  GitBranch,
  MessageSquare,
  Building2,
  Users,
  FolderKanban,
  Bell
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useStore } from '@/store/useStore'
import { Badge } from '@/components/ui/badge'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Setup', href: '/setup', icon: Settings },
  { name: 'Workflow', href: '/workflow', icon: GitBranch },
  { name: 'Chat', href: '/chat', icon: MessageSquare },
]

export default function Layout() {
  const location = useLocation()
  const { companyState, interrupts } = useStore()

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 border-r bg-card flex flex-col">
        {/* Logo */}
        <div className="h-16 flex items-center px-6 border-b">
          <Building2 className="h-8 w-8 text-primary" />
          <span className="ml-3 text-xl font-bold">AI Company</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-4 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  'flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )}
              >
                <item.icon className="h-5 w-5 mr-3" />
                {item.name}
                {item.name === 'Chat' && interrupts.length > 0 && (
                  <Badge variant="destructive" className="ml-auto">
                    {interrupts.length}
                  </Badge>
                )}
              </Link>
            )
          })}
        </nav>

        {/* Status */}
        <div className="p-4 border-t">
          <div className="bg-secondary rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Status</span>
              <Badge variant={companyState?.should_continue ? 'success' : 'secondary'}>
                {companyState?.current_phase || 'Not Started'}
              </Badge>
            </div>
            <div className="space-y-1 text-xs text-muted-foreground">
              <div className="flex justify-between">
                <span>Agents</span>
                <span>{companyState?.agents_count || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Projects</span>
                <span>{companyState?.projects_count || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Tasks</span>
                <span>{companyState?.tasks_count || 0}</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 border-b flex items-center justify-between px-6">
          <div>
            <h1 className="text-lg font-semibold">
              {navigation.find(n => n.href === location.pathname)?.name || 'AI Company'}
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            {interrupts.length > 0 && (
              <Link to="/chat" className="relative">
                <Bell className="h-5 w-5 text-muted-foreground hover:text-foreground" />
                <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 rounded-full text-[10px] text-white flex items-center justify-center">
                  {interrupts.length}
                </span>
              </Link>
            )}
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-muted-foreground" />
              <span className="text-sm">CEO</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-auto">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
