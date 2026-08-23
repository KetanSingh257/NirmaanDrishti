import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { fetchFilters, fetchProject, fetchProjectOptions, predictCost } from '../lib/api'
import type { CostPrediction, Project } from '../lib/types'
import { inrCr, pct } from '../lib/format'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Field, Input, Select } from '../components/ui/Input'
import { ProjectPicker } from '../components/shared/ProjectPicker'
import { RiskBadge } from '../components/ui/Badge'
import { PageHeader } from '../components/shared/PageHeader'
import { AnalyzeOverlay } from '../components/shared/AnalyzeOverlay'

const empty = {
  original_cost_cr: 12000,
  revised_cost_cr: 14800,
  current_expenditure_cr: 8200,
  physical_progress_pct: 48,
  previous_progress: 44,
  previous_expenditure: 7100,
  project_age_days: 980,
  days_to_original_completion: -40,
  days_overdue: 40,
  agency: 'NHAI',
  state: 'Maharashtra',
}

export default function CostAnalysis() {
  const [form, setForm] = useState(empty)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<CostPrediction | null>(null)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState('')

  const list = useQuery({
    queryKey: ['projects-mini'],
    queryFn: fetchProjectOptions,
  })
  const filters = useQuery({ queryKey: ['filters'], queryFn: fetchFilters })

  useEffect(() => {
    if (!selected) return
    fetchProject(selected).then((p: Project) => {
      setForm({
        original_cost_cr: p.original_cost_cr,
        revised_cost_cr: p.revised_cost_cr,
        current_expenditure_cr: p.current_expenditure_cr,
        physical_progress_pct: p.physical_progress_pct,
        previous_progress: p.previous_progress,
        previous_expenditure: p.previous_expenditure,
        project_age_days: p.project_age_days,
        days_to_original_completion: p.days_to_original_completion,
        days_overdue: p.days_overdue,
        agency: p.agency,
        state: p.state,
      })
      setResult(null)
    })
  }, [selected])

  const set = (key: keyof typeof empty) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const v = e.target.value
    setForm((f) => ({ ...f, [key]: numericKeys.has(key) ? Number(v) : v }))
  }

  const run = async () => {
    setBusy(true)
    setError('')
    try {
      await wait(2200)
      const data = await predictCost(form)
      setResult(data)
    } catch {
      setError('Prediction service failed. Confirm the API is running.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Engine 01"
        title="Cost intelligence"
        subtitle="Predict remaining expenditure and overrun risk. Swap in a trained model without changing this screen."
      />

      <div className="grid gap-6 lg:grid-cols-5">
        <Card className="p-5 lg:col-span-2">
          <ProjectPicker label="Load a monitored project" projects={list.data ?? []} selected={selected} onSelect={setSelected} />
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <Field label="Original cost (Cr)"><Input type="number" value={form.original_cost_cr} onChange={set('original_cost_cr')} /></Field>
            <Field label="Revised cost (Cr)"><Input type="number" value={form.revised_cost_cr} onChange={set('revised_cost_cr')} /></Field>
            <Field label="Current expenditure"><Input type="number" value={form.current_expenditure_cr} onChange={set('current_expenditure_cr')} /></Field>
            <Field label="Physical progress %"><Input type="number" value={form.physical_progress_pct} onChange={set('physical_progress_pct')} /></Field>
            <Field label="Previous progress"><Input type="number" value={form.previous_progress} onChange={set('previous_progress')} /></Field>
            <Field label="Previous expenditure"><Input type="number" value={form.previous_expenditure} onChange={set('previous_expenditure')} /></Field>
            <Field label="Project age (days)"><Input type="number" value={form.project_age_days} onChange={set('project_age_days')} /></Field>
            <Field label="Days to original completion"><Input type="number" value={form.days_to_original_completion} onChange={set('days_to_original_completion')} /></Field>
            <Field label="Days overdue"><Input type="number" value={form.days_overdue} onChange={set('days_overdue')} /></Field>
            <Field label="Agency">
              <Select value={form.agency} onChange={set('agency')}>
                {(filters.data?.agencies ?? [form.agency]).map((a) => <option key={a}>{a}</option>)}
              </Select>
            </Field>
            <Field label="State">
              <Select value={form.state} onChange={set('state')}>
                {(filters.data?.states ?? [form.state]).map((a) => <option key={a}>{a}</option>)}
              </Select>
            </Field>
          </div>
          <Button className="mt-5 w-full" onClick={run} disabled={busy}>
            Run Cost Intelligence
          </Button>
        </Card>

        <div className="relative lg:col-span-3">
          <AnalyzeOverlay
            active={busy}
            steps={[
              'Analyzing project variables…',
              'Evaluating expenditure patterns…',
              'Calculating cost risk…',
              'Generating prediction…',
            ]}
          />
          <AnimatePresence mode="wait">
            {result ? (
              <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <Card className="p-8">
                  <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-parchment-300/70">
                    Predicted expenditure
                  </p>
                  <p className="mt-2 font-display text-5xl">{inrCr(result.predicted_expenditure_cr)}</p>
                  <p className="mt-2 text-sm text-parchment-200/50">
                    {result.model_name}
                    {result.used_real_model ? ' · live model' : ' · heuristic stand-in'}
                  </p>
                </Card>
                <div className="grid gap-3 sm:grid-cols-2">
                  <StatCard label="Current expenditure" value={inrCr(result.current_expenditure_cr)} />
                  <StatCard label="Potential overrun" value={inrCr(result.predicted_overrun_cr)} />
                  <StatCard label="Overrun %" value={pct(result.overrun_percentage)} />
                  <StatCard label="Confidence" value={`${result.confidence_score}%`} />
                </div>
                <div>
                  <RiskBadge level={result.risk_level} />
                </div>
                <Card className="p-6">
                  <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-parchment-300/70">
                    Why this prediction?
                  </p>
                  <ul className="mt-4 space-y-3">
                    {result.explanations.map((e) => (
                      <li key={e} className="text-sm text-parchment-100/80">• {e}</li>
                    ))}
                  </ul>
                </Card>
              </motion.div>
            ) : (
              <Card className="flex min-h-[360px] items-center justify-center p-8 text-center text-sm text-parchment-200/45">
                {error || 'Configure inputs and run the cost engine.'}
              </Card>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}

const numericKeys = new Set([
  'original_cost_cr',
  'revised_cost_cr',
  'current_expenditure_cr',
  'physical_progress_pct',
  'previous_progress',
  'previous_expenditure',
  'project_age_days',
  'days_to_original_completion',
  'days_overdue',
])

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <Card className="p-4">
      <p className="font-mono text-[9px] uppercase tracking-[0.16em] text-parchment-200/70">{label}</p>
      <p className="mt-1 text-lg tabular-nums">{value}</p>
    </Card>
  )
}

function wait(ms: number) {
  return new Promise((r) => setTimeout(r, ms))
}
