import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { fetchFilters, fetchProject, fetchProjectOptions, predictTime } from '../lib/api'
import type { Project, TimePrediction } from '../lib/types'
import { daysLabel, prettyDate } from '../lib/format'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Field, Input, Select } from '../components/ui/Input'
import { RiskBadge } from '../components/ui/Badge'
import { PageHeader } from '../components/shared/PageHeader'
import { AnalyzeOverlay } from '../components/shared/AnalyzeOverlay'
import { ProjectPicker } from '../components/shared/ProjectPicker'

const empty = {
  physical_progress_pct: 48,
  previous_progress: 44,
  project_age_days: 980,
  days_to_original_completion: -40,
  days_overdue: 40,
  original_cost_cr: 12000,
  revised_cost_cr: 14800,
  agency: 'NHAI',
  state: 'Maharashtra',
}

export default function TimeAnalysis() {
  const [form, setForm] = useState(empty)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<TimePrediction | null>(null)
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
        physical_progress_pct: p.physical_progress_pct,
        previous_progress: p.previous_progress,
        project_age_days: p.project_age_days,
        days_to_original_completion: p.days_to_original_completion,
        days_overdue: p.days_overdue,
        original_cost_cr: p.original_cost_cr,
        revised_cost_cr: p.revised_cost_cr,
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
      setResult(await predictTime(form))
    } catch {
      setError('Time engine failed. Confirm the API is running.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Engine 02"
        title="Time intelligence"
        subtitle="Estimate delay risk and a realistic completion window from current velocity."
      />
      <div className="grid gap-6 lg:grid-cols-5">
        <Card className="p-5 lg:col-span-2">
          <ProjectPicker label="Load a monitored project" projects={list.data ?? []} selected={selected} onSelect={setSelected} />
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <Field label="Physical progress %"><Input type="number" value={form.physical_progress_pct} onChange={set('physical_progress_pct')} /></Field>
            <Field label="Previous progress"><Input type="number" value={form.previous_progress} onChange={set('previous_progress')} /></Field>
            <Field label="Project age (days)"><Input type="number" value={form.project_age_days} onChange={set('project_age_days')} /></Field>
            <Field label="Days to original completion"><Input type="number" value={form.days_to_original_completion} onChange={set('days_to_original_completion')} /></Field>
            <Field label="Days overdue"><Input type="number" value={form.days_overdue} onChange={set('days_overdue')} /></Field>
            <Field label="Original cost"><Input type="number" value={form.original_cost_cr} onChange={set('original_cost_cr')} /></Field>
            <Field label="Revised cost"><Input type="number" value={form.revised_cost_cr} onChange={set('revised_cost_cr')} /></Field>
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
          <Button className="mt-5 w-full" onClick={run} disabled={busy}>Run Time Intelligence</Button>
        </Card>

        <div className="relative lg:col-span-3">
          <AnalyzeOverlay
            active={busy}
            steps={[
              'Reading schedule baseline…',
              'Measuring progress velocity…',
              'Simulating remaining duration…',
              'Scoring delay probability…',
            ]}
          />
          <AnimatePresence mode="wait">
            {result ? (
              <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <Card className="p-8">
                  <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-parchment-300/70">Predicted delay</p>
                  <p className="mt-2 font-display text-5xl">{result.predicted_delay_days} days</p>
                  <p className="mt-2 text-sm text-parchment-200/50">{result.model_name}</p>
                </Card>
                <div className="grid gap-3 sm:grid-cols-2">
                  <Stat label="Estimated completion" value={prettyDate(result.estimated_completion_date)} />
                  <Stat label="Delay probability" value={`${result.delay_probability}%`} />
                  <Stat label="Remaining days" value={daysLabel(result.remaining_days)} />
                  <Stat label="Confidence" value={`${result.confidence_score}%`} />
                </div>
                <RiskBadge level={result.risk_level} />
                <Timeline remaining={result.remaining_days} delay={result.predicted_delay_days} />
                <Card className="p-6">
                  <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-parchment-300/70">Why this prediction?</p>
                  <ul className="mt-4 space-y-3">
                    {result.explanations.map((e) => <li key={e} className="text-sm">• {e}</li>)}
                  </ul>
                </Card>
              </motion.div>
            ) : (
              <Card className="flex min-h-[360px] items-center justify-center p-8 text-center text-sm text-parchment-200/45">
                {error || 'Configure inputs and run the time engine.'}
              </Card>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}

const numericKeys = new Set([
  'physical_progress_pct',
  'previous_progress',
  'project_age_days',
  'days_to_original_completion',
  'days_overdue',
  'original_cost_cr',
  'revised_cost_cr',
])

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <Card className="p-4">
      <p className="font-mono text-[9px] uppercase tracking-[0.16em] text-parchment-200/70">{label}</p>
      <p className="mt-1 text-lg tabular-nums">{value}</p>
    </Card>
  )
}

function Timeline({ remaining, delay }: { remaining: number; delay: number }) {
  return (
    <Card className="p-6">
      <p className="mb-4 font-mono text-[10px] uppercase tracking-[0.2em] text-parchment-300/70">Timeline</p>
      <div className="relative h-2 rounded-full bg-parchment-300/10">
        <div className="absolute left-0 top-1/2 h-3 w-3 -translate-y-1/2 rounded-full bg-parchment-300" />
        <div className="absolute left-1/2 top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-signal-cyan" />
        <div className="absolute right-0 top-1/2 h-3 w-3 -translate-y-1/2 rounded-full bg-signal-rose" />
      </div>
      <div className="mt-3 grid grid-cols-3 text-[11px] text-parchment-200/55">
        <span>Project start</span>
        <span className="text-center">Current date</span>
        <span className="text-right">Predicted completion</span>
      </div>
      <p className="mt-3 text-xs text-parchment-200/45">
        {remaining} days remaining · {delay} days of forecast slip versus the original sanction.
      </p>
    </Card>
  )
}

function wait(ms: number) {
  return new Promise((r) => setTimeout(r, ms))
}
