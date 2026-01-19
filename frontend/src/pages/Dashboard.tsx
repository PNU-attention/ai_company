import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Users,
  FolderKanban,
  CheckSquare,
  AlertCircle,
  ArrowRight,
  Play,
  Clock,
  CheckCircle
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useStore } from '@/store/useStore'

export default function Dashboard() {
  const {
    companyState,
    agents,
    projects,
    tasks,
    interrupts,
    fetchState,
    fetchAgents,
    fetchProjects,
    fetchTasks,
    fetchInterrupts,
    sessionId
  } = useStore()

  useEffect(() => {
    if (sessionId) {
      fetchState()
      fetchAgents()
      fetchProjects()
      fetchTasks()
      fetchInterrupts()
    }
  }, [sessionId])

  const stats = [
    {
      name: 'Active Agents',
      value: agents.length,
      icon: Users,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
    },
    {
      name: 'Projects',
      value: projects.length,
      icon: FolderKanban,
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
    },
    {
      name: 'Tasks',
      value: tasks.length,
      icon: CheckSquare,
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/10',
    },
    {
      name: 'Pending Actions',
      value: interrupts.length,
      icon: AlertCircle,
      color: 'text-orange-500',
      bgColor: 'bg-orange-500/10',
    },
  ]

  const getTaskStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'EXECUTING':
        return <Play className="h-4 w-4 text-yellow-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Welcome Section */}
      {!companyState?.ceo_request && (
        <Card className="bg-gradient-to-r from-purple-500/10 to-blue-500/10 border-purple-500/20">
          <CardHeader>
            <CardTitle>Welcome to AI Company</CardTitle>
            <CardDescription>
              Start by setting up your company goals and KPIs. Our AI agents will help you achieve them.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/setup">
              <Button>
                Get Started
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {/* Company Goal */}
      {companyState?.ceo_request && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Company Goal</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xl font-semibold">{companyState.ceo_request.goal}</p>
            {companyState.ceo_request.kpis && companyState.ceo_request.kpis.length > 0 && (
              <div className="mt-4">
                <p className="text-sm text-muted-foreground mb-2">KPIs:</p>
                <div className="flex flex-wrap gap-2">
                  {companyState.ceo_request.kpis.map((kpi, i) => (
                    <Badge key={i} variant="secondary">{kpi}</Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.name}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{stat.name}</p>
                  <p className="text-3xl font-bold mt-1">{stat.value}</p>
                </div>
                <div className={`p-3 rounded-full ${stat.bgColor}`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Agents */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">Active Agents</CardTitle>
            <Link to="/workflow">
              <Button variant="ghost" size="sm">
                View All
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {agents.length === 0 ? (
              <p className="text-sm text-muted-foreground">No agents created yet</p>
            ) : (
              <div className="space-y-3">
                {agents.slice(0, 5).map((agent) => (
                  <div
                    key={agent.id}
                    className="flex items-center justify-between p-3 rounded-lg bg-secondary/50"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="p-2 rounded-lg bg-primary/10">
                        <Users className="h-4 w-4 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium text-sm">{agent.role_name}</p>
                        <p className="text-xs text-muted-foreground">
                          {agent.specialties?.slice(0, 2).join(', ')}
                        </p>
                      </div>
                    </div>
                    <Badge
                      variant={agent.status === 'active' ? 'success' : 'secondary'}
                    >
                      {agent.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Tasks */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">Recent Tasks</CardTitle>
            <Link to="/workflow">
              <Button variant="ghost" size="sm">
                View All
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {tasks.length === 0 ? (
              <p className="text-sm text-muted-foreground">No tasks created yet</p>
            ) : (
              <div className="space-y-3">
                {tasks.slice(0, 5).map((task) => (
                  <div
                    key={task.id}
                    className="flex items-center justify-between p-3 rounded-lg bg-secondary/50"
                  >
                    <div className="flex items-center space-x-3">
                      {getTaskStatusIcon(task.status)}
                      <div>
                        <p className="font-medium text-sm">{task.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {task.assigned_to || 'Unassigned'}
                        </p>
                      </div>
                    </div>
                    <Badge variant="outline">{task.status}</Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Pending Interrupts */}
      {interrupts.length > 0 && (
        <Card className="border-orange-500/50">
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              <AlertCircle className="h-5 w-5 mr-2 text-orange-500" />
              Action Required
            </CardTitle>
            <CardDescription>
              The following items require your attention
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {interrupts.map((interrupt) => (
                <div
                  key={interrupt.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-orange-500/30 bg-orange-500/5"
                >
                  <div>
                    <p className="font-medium">{interrupt.message}</p>
                    <p className="text-sm text-muted-foreground">
                      From: {interrupt.from_agent} • Type: {interrupt.type}
                    </p>
                  </div>
                  <Link to="/chat">
                    <Button size="sm">
                      Respond
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
