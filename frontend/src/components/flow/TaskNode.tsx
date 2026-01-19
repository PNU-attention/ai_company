import { memo } from 'react'
import { Handle, Position } from '@xyflow/react'
import { FileText, Play, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'

interface TaskNodeData {
  label: string
  description: string
  status: string
  statusColor: string
  taskType: string
  assignedTo?: string
}

interface TaskNodeProps {
  data: TaskNodeData
  selected: boolean
}

const TaskNode = memo(({ data, selected }: TaskNodeProps) => {
  const getStatusIcon = () => {
    switch (data.status) {
      case 'COMPLETED':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'FAILED':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'EXECUTING':
        return <Play className="h-4 w-4 text-yellow-500" />
      case 'INPUT_REQUIRED':
      case 'APPROVAL_WAIT':
        return <AlertCircle className="h-4 w-4 text-blue-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getTaskTypeIcon = () => {
    switch (data.taskType) {
      case 'ACTION':
        return <Play className="h-5 w-5" />
      case 'DOCUMENT':
        return <FileText className="h-5 w-5" />
      default:
        return <FileText className="h-5 w-5" />
    }
  }

  return (
    <div
      className={cn(
        'px-4 py-3 rounded-lg border bg-card min-w-[160px] transition-all',
        selected && 'ring-2 ring-primary ring-offset-2 ring-offset-background',
        data.status === 'EXECUTING' && 'border-yellow-500',
        data.status === 'COMPLETED' && 'border-green-500',
        data.status === 'FAILED' && 'border-red-500'
      )}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!bg-primary !w-3 !h-3"
      />

      <div className="flex items-start space-x-3">
        <div className="p-1.5 rounded bg-secondary">
          {getTaskTypeIcon()}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2">
            <span className="font-medium text-sm truncate">{data.label}</span>
            {getStatusIcon()}
          </div>
          <p className="text-xs text-muted-foreground truncate mt-0.5">
            {data.description}
          </p>
        </div>
      </div>

      <div className="mt-2 flex items-center justify-between">
        <Badge
          variant="outline"
          className="text-[10px]"
          style={{ borderColor: data.statusColor, color: data.statusColor }}
        >
          {data.status}
        </Badge>
        {data.taskType && (
          <Badge variant="secondary" className="text-[10px]">
            {data.taskType}
          </Badge>
        )}
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="!bg-primary !w-3 !h-3"
      />
    </div>
  )
})

TaskNode.displayName = 'TaskNode'

export default TaskNode
