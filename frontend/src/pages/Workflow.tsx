import { useEffect } from 'react'
import { useStore } from '@/store/useStore'
import WorkflowCanvas from '@/components/flow/WorkflowCanvas'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { RefreshCw, Users, FolderKanban, CheckSquare } from 'lucide-react'

export default function Workflow() {
  const {
    fetchGraph,
    fetchAgents,
    fetchProjects,
    fetchTasks,
    agents,
    projects,
    tasks,
    graphNodes,
    sessionId,
    isLoading
  } = useStore()

  useEffect(() => {
    if (sessionId) {
      fetchGraph()
      fetchAgents()
      fetchProjects()
      fetchTasks()
    }
  }, [sessionId])

  const handleRefresh = () => {
    fetchGraph()
    fetchAgents()
    fetchProjects()
    fetchTasks()
  }

  return (
    <div className="h-full flex">
      {/* Main Canvas */}
      <div className="flex-1 relative">
        {graphNodes.length > 0 ? (
          <WorkflowCanvas />
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <p className="text-muted-foreground mb-4">
                No workflow data yet. Set up your company to see the agent workflow.
              </p>
              <Button onClick={handleRefresh} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        )}

        {/* Refresh Button */}
        <Button
          variant="outline"
          size="icon"
          className="absolute top-4 right-4"
          onClick={handleRefresh}
          disabled={isLoading}
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
        </Button>
      </div>

      {/* Right Sidebar */}
      <aside className="w-80 border-l bg-card overflow-auto">
        <div className="p-4 space-y-4">
          {/* Agents Panel */}
          <Card>
            <CardHeader className="py-3">
              <CardTitle className="text-sm flex items-center">
                <Users className="h-4 w-4 mr-2" />
                Agents ({agents.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="py-2">
              {agents.length === 0 ? (
                <p className="text-xs text-muted-foreground">No agents</p>
              ) : (
                <div className="space-y-2">
                  {agents.map((agent) => (
                    <div
                      key={agent.id}
                      className="p-2 rounded-lg bg-secondary/50 text-sm"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{agent.role_name}</span>
                        <Badge
                          variant={agent.status === 'active' ? 'success' : 'secondary'}
                          className="text-[10px]"
                        >
                          {agent.status}
                        </Badge>
                      </div>
                      {agent.specialties && agent.specialties.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {agent.specialties.slice(0, 3).map((s, i) => (
                            <Badge key={i} variant="outline" className="text-[10px] px-1">
                              {s}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Projects Panel */}
          <Card>
            <CardHeader className="py-3">
              <CardTitle className="text-sm flex items-center">
                <FolderKanban className="h-4 w-4 mr-2" />
                Projects ({projects.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="py-2">
              {projects.length === 0 ? (
                <p className="text-xs text-muted-foreground">No projects</p>
              ) : (
                <div className="space-y-2">
                  {projects.map((project) => (
                    <div
                      key={project.id}
                      className="p-2 rounded-lg bg-secondary/50 text-sm"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{project.name}</span>
                        <Badge variant="outline" className="text-[10px]">
                          {project.status}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                        {project.description}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Tasks Panel */}
          <Card>
            <CardHeader className="py-3">
              <CardTitle className="text-sm flex items-center">
                <CheckSquare className="h-4 w-4 mr-2" />
                Tasks ({tasks.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="py-2">
              {tasks.length === 0 ? (
                <p className="text-xs text-muted-foreground">No tasks</p>
              ) : (
                <div className="space-y-2 max-h-96 overflow-auto">
                  {tasks.map((task) => (
                    <div
                      key={task.id}
                      className="p-2 rounded-lg bg-secondary/50 text-sm"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-xs">{task.name}</span>
                        <Badge
                          variant={
                            task.status === 'COMPLETED'
                              ? 'success'
                              : task.status === 'FAILED'
                              ? 'destructive'
                              : 'outline'
                          }
                          className="text-[10px]"
                        >
                          {task.status}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between mt-1">
                        <span className="text-[10px] text-muted-foreground">
                          {task.assigned_to || 'Unassigned'}
                        </span>
                        <Badge variant="secondary" className="text-[10px]">
                          {task.type}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </aside>
    </div>
  )
}
