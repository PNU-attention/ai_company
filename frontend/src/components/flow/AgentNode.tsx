import { memo } from 'react'
import { Handle, Position } from '@xyflow/react'
import { Bot, User, Briefcase, Cpu } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'

interface AgentNodeData {
  label: string
  role: string
  status: string
  agentType: 'hr' | 'rm' | 'expert' | 'ceo'
  specialties?: string[]
  tools?: string[]
}

interface AgentNodeProps {
  data: AgentNodeData
  selected: boolean
}

const AgentNode = memo(({ data, selected }: AgentNodeProps) => {
  const getIcon = () => {
    switch (data.agentType) {
      case 'ceo':
        return <User className="h-6 w-6" />
      case 'hr':
        return <Briefcase className="h-6 w-6" />
      case 'rm':
        return <Cpu className="h-6 w-6" />
      default:
        return <Bot className="h-6 w-6" />
    }
  }

  const getStatusColor = () => {
    switch (data.status) {
      case 'active':
        return 'bg-green-500'
      case 'busy':
        return 'bg-yellow-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getBgColor = () => {
    switch (data.agentType) {
      case 'ceo':
        return 'bg-purple-900/50 border-purple-500'
      case 'hr':
        return 'bg-blue-900/50 border-blue-500'
      case 'rm':
        return 'bg-green-900/50 border-green-500'
      default:
        return 'bg-card border-border'
    }
  }

  return (
    <div
      className={cn(
        'px-4 py-3 rounded-xl border-2 min-w-[180px] transition-all',
        getBgColor(),
        selected && 'ring-2 ring-primary ring-offset-2 ring-offset-background'
      )}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!bg-primary !w-3 !h-3"
      />

      <div className="flex items-center space-x-3">
        <div className="p-2 rounded-lg bg-background/50">
          {getIcon()}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2">
            <span className="font-medium truncate">{data.label}</span>
            <span className={cn('w-2 h-2 rounded-full', getStatusColor())} />
          </div>
          <p className="text-xs text-muted-foreground truncate">{data.role}</p>
        </div>
      </div>

      {data.specialties && data.specialties.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {data.specialties.slice(0, 2).map((specialty, i) => (
            <Badge key={i} variant="secondary" className="text-[10px] px-1.5 py-0">
              {specialty}
            </Badge>
          ))}
          {data.specialties.length > 2 && (
            <Badge variant="outline" className="text-[10px] px-1.5 py-0">
              +{data.specialties.length - 2}
            </Badge>
          )}
        </div>
      )}

      <Handle
        type="source"
        position={Position.Right}
        className="!bg-primary !w-3 !h-3"
      />
    </div>
  )
})

AgentNode.displayName = 'AgentNode'

export default AgentNode
