import { useState, useEffect, useRef } from 'react'
import { Send, Bot, User, AlertCircle, CheckCircle, XCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { useStore } from '@/store/useStore'
import { cn } from '@/lib/utils'

export default function Chat() {
  const {
    chatMessages,
    interrupts,
    agents,
    selectedAgent,
    setSelectedAgent,
    sendChatMessage,
    respondToInterrupt,
    fetchInterrupts,
    sessionId,
    isLoading
  } = useStore()

  const [inputValue, setInputValue] = useState('')
  const [interruptInputs, setInterruptInputs] = useState<Record<string, string>>({})
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (sessionId) {
      fetchInterrupts()
    }
  }, [sessionId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages])

  const handleSend = () => {
    if (!inputValue.trim()) return
    sendChatMessage(inputValue, selectedAgent || undefined)
    setInputValue('')
  }

  const handleInterruptResponse = async (interruptId: string, approved?: boolean) => {
    const inputs: Record<string, unknown> = {}

    // Collect inputs for this interrupt
    Object.keys(interruptInputs).forEach((key) => {
      if (key.startsWith(interruptId + '_')) {
        const inputKey = key.replace(interruptId + '_', '')
        inputs[inputKey] = interruptInputs[key]
      }
    })

    await respondToInterrupt(interruptId, {
      approved,
      inputs: Object.keys(inputs).length > 0 ? inputs : undefined,
    })

    // Clear inputs
    const newInputs = { ...interruptInputs }
    Object.keys(newInputs).forEach((key) => {
      if (key.startsWith(interruptId + '_')) {
        delete newInputs[key]
      }
    })
    setInterruptInputs(newInputs)
  }

  return (
    <div className="h-full flex">
      {/* Agent Selector Sidebar */}
      <aside className="w-64 border-r bg-card">
        <div className="p-4">
          <h3 className="font-semibold mb-4">Agents</h3>
          <div className="space-y-2">
            <button
              onClick={() => setSelectedAgent(null)}
              className={cn(
                'w-full p-3 rounded-lg text-left transition-colors',
                !selectedAgent
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-secondary'
              )}
            >
              <div className="flex items-center space-x-2">
                <Bot className="h-4 w-4" />
                <span className="text-sm font-medium">All Agents</span>
              </div>
            </button>
            {agents.map((agent) => (
              <button
                key={agent.id}
                onClick={() => setSelectedAgent(agent.id)}
                className={cn(
                  'w-full p-3 rounded-lg text-left transition-colors',
                  selectedAgent === agent.id
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-secondary'
                )}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Bot className="h-4 w-4" />
                    <span className="text-sm font-medium">{agent.role_name}</span>
                  </div>
                  <Badge
                    variant={agent.status === 'active' ? 'success' : 'secondary'}
                    className="text-[10px]"
                  >
                    {agent.status}
                  </Badge>
                </div>
              </button>
            ))}
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Pending Interrupts */}
        {interrupts.length > 0 && (
          <div className="p-4 border-b bg-orange-500/5">
            <h3 className="font-semibold mb-3 flex items-center">
              <AlertCircle className="h-4 w-4 mr-2 text-orange-500" />
              Action Required ({interrupts.length})
            </h3>
            <div className="space-y-3">
              {interrupts.map((interrupt) => (
                <Card key={interrupt.id} className="border-orange-500/30">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <p className="font-medium">{interrupt.message}</p>
                        <p className="text-sm text-muted-foreground">
                          From: {interrupt.from_agent} • Type: {interrupt.type}
                        </p>
                      </div>
                      <Badge variant="warning">{interrupt.type}</Badge>
                    </div>

                    {/* Required Inputs */}
                    {interrupt.required_inputs && interrupt.required_inputs.length > 0 && (
                      <div className="space-y-3 mb-4">
                        {interrupt.required_inputs.map((input) => (
                          <div key={input.key}>
                            <label className="block text-sm font-medium mb-1">
                              {input.label}
                              {input.description && (
                                <span className="text-muted-foreground font-normal ml-2">
                                  ({input.description})
                                </span>
                              )}
                            </label>
                            <Input
                              value={interruptInputs[`${interrupt.id}_${input.key}`] || ''}
                              onChange={(e) =>
                                setInterruptInputs({
                                  ...interruptInputs,
                                  [`${interrupt.id}_${input.key}`]: e.target.value,
                                })
                              }
                              placeholder={input.example || `Enter ${input.label}`}
                            />
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex space-x-2">
                      {interrupt.type === 'approval_request' ? (
                        <>
                          <Button
                            size="sm"
                            onClick={() => handleInterruptResponse(interrupt.id, true)}
                            disabled={isLoading}
                          >
                            <CheckCircle className="h-4 w-4 mr-1" />
                            Approve
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleInterruptResponse(interrupt.id, false)}
                            disabled={isLoading}
                          >
                            <XCircle className="h-4 w-4 mr-1" />
                            Reject
                          </Button>
                        </>
                      ) : (
                        <Button
                          size="sm"
                          onClick={() => handleInterruptResponse(interrupt.id)}
                          disabled={isLoading}
                        >
                          Submit
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-auto p-4">
          <div className="space-y-4 max-w-3xl mx-auto">
            {chatMessages.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No messages yet. Start a conversation with your AI agents.</p>
              </div>
            ) : (
              chatMessages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    'flex',
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  <div
                    className={cn(
                      'max-w-[80%] rounded-lg p-4',
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary'
                    )}
                  >
                    <div className="flex items-center space-x-2 mb-1">
                      {message.role === 'user' ? (
                        <User className="h-4 w-4" />
                      ) : (
                        <Bot className="h-4 w-4" />
                      )}
                      <span className="text-xs font-medium">
                        {message.role === 'user'
                          ? 'You (CEO)'
                          : message.agentName || 'System'}
                      </span>
                      <span className="text-xs opacity-60">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <div className="p-4 border-t bg-card">
          <div className="max-w-3xl mx-auto flex space-x-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={
                selectedAgent
                  ? `Message ${agents.find((a) => a.id === selectedAgent)?.role_name}...`
                  : 'Message all agents...'
              }
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            />
            <Button onClick={handleSend} disabled={!inputValue.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
