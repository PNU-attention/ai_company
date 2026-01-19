import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, X, Loader2, Target, TrendingUp, AlertTriangle, Calendar, DollarSign } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { useStore } from '@/store/useStore'

export default function Setup() {
  const navigate = useNavigate()
  const { setupCompany, isLoading, error } = useStore()

  const [goal, setGoal] = useState('')
  const [kpis, setKpis] = useState<string[]>([])
  const [newKpi, setNewKpi] = useState('')
  const [constraints, setConstraints] = useState<string[]>([])
  const [newConstraint, setNewConstraint] = useState('')
  const [context, setContext] = useState('')
  const [budget, setBudget] = useState('')
  const [timeline, setTimeline] = useState('')

  const addKpi = () => {
    if (newKpi.trim()) {
      setKpis([...kpis, newKpi.trim()])
      setNewKpi('')
    }
  }

  const removeKpi = (index: number) => {
    setKpis(kpis.filter((_, i) => i !== index))
  }

  const addConstraint = () => {
    if (newConstraint.trim()) {
      setConstraints([...constraints, newConstraint.trim()])
      setNewConstraint('')
    }
  }

  const removeConstraint = (index: number) => {
    setConstraints(constraints.filter((_, i) => i !== index))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!goal.trim()) return

    await setupCompany({
      goal,
      kpis,
      constraints,
      context: context || undefined,
      budget: budget || undefined,
      timeline: timeline || undefined,
    })

    navigate('/workflow')
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Company Setup</h1>
        <p className="text-muted-foreground mt-2">
          Define your company's goals and constraints. Our AI agents will create a plan to achieve them.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Goal */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Target className="h-5 w-5 mr-2" />
              Company Goal
            </CardTitle>
            <CardDescription>
              What do you want your AI company to achieve?
            </CardDescription>
          </CardHeader>
          <CardContent>
            <textarea
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="예: 쿠팡에 입점하여 월 매출 1000만원 달성"
              className="w-full h-24 px-3 py-2 rounded-md border bg-background resize-none focus:outline-none focus:ring-2 focus:ring-ring"
              required
            />
          </CardContent>
        </Card>

        {/* KPIs */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="h-5 w-5 mr-2" />
              Key Performance Indicators (KPIs)
            </CardTitle>
            <CardDescription>
              How will you measure success?
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex space-x-2 mb-4">
              <Input
                value={newKpi}
                onChange={(e) => setNewKpi(e.target.value)}
                placeholder="예: 월 매출 1000만원"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addKpi())}
              />
              <Button type="button" onClick={addKpi} variant="secondary">
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {kpis.map((kpi, i) => (
                <Badge key={i} variant="secondary" className="px-3 py-1">
                  {kpi}
                  <button
                    type="button"
                    onClick={() => removeKpi(i)}
                    className="ml-2 hover:text-destructive"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Constraints */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertTriangle className="h-5 w-5 mr-2" />
              Constraints
            </CardTitle>
            <CardDescription>
              What limitations should be considered?
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex space-x-2 mb-4">
              <Input
                value={newConstraint}
                onChange={(e) => setNewConstraint(e.target.value)}
                placeholder="예: 초기 투자 500만원 이내"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addConstraint())}
              />
              <Button type="button" onClick={addConstraint} variant="secondary">
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {constraints.map((constraint, i) => (
                <Badge key={i} variant="outline" className="px-3 py-1">
                  {constraint}
                  <button
                    type="button"
                    onClick={() => removeConstraint(i)}
                    className="ml-2 hover:text-destructive"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Additional Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-base">
                <DollarSign className="h-5 w-5 mr-2" />
                Budget
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Input
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                placeholder="예: 500만원"
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-base">
                <Calendar className="h-5 w-5 mr-2" />
                Timeline
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Input
                value={timeline}
                onChange={(e) => setTimeline(e.target.value)}
                placeholder="예: 3개월"
              />
            </CardContent>
          </Card>
        </div>

        {/* Context */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Additional Context</CardTitle>
            <CardDescription>
              Any other information that might be helpful
            </CardDescription>
          </CardHeader>
          <CardContent>
            <textarea
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="예: 패션 액세서리 판매 예정, 대학생 타겟"
              className="w-full h-24 px-3 py-2 rounded-md border bg-background resize-none focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </CardContent>
        </Card>

        {/* Error Display */}
        {error && (
          <div className="p-4 rounded-lg bg-destructive/10 border border-destructive text-destructive">
            {error}
          </div>
        )}

        {/* Submit */}
        <div className="flex justify-end">
          <Button type="submit" size="lg" disabled={!goal.trim() || isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              'Start AI Company'
            )}
          </Button>
        </div>
      </form>
    </div>
  )
}
