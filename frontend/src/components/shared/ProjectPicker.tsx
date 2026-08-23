import { useState } from 'react'
import { Field, Input } from '../ui/Input'
import type { ProjectOption } from '../../lib/types'

type ProjectPickerProps = {
  label: string
  projects: ProjectOption[]
  selected: string
  onSelect: (projectId: string) => void
}

export function ProjectPicker({ label, projects, selected, onSelect }: ProjectPickerProps) {
  const [search, setSearch] = useState('')
  const [open, setOpen] = useState(false)
  const selectedName = projects.find((project) => String(project.id) === selected)?.project_name
  const filteredProjects = projects.filter((project) =>
    project.project_name.toLowerCase().includes(search.trim().toLowerCase()),
  )

  return (
    <Field label={label}>
      <div className="relative">
        <Input
          type="search"
          value={search}
          placeholder={selectedName ?? 'Search monitored projects...'}
          onFocus={() => setOpen(true)}
          onChange={(event) => {
            setSearch(event.target.value)
            setOpen(true)
          }}
          onBlur={() => window.setTimeout(() => setOpen(false), 120)}
          role="combobox"
          aria-expanded={open}
          aria-controls={`${label.replace(/\s+/g, '-').toLowerCase()}-options`}
        />
        {open && (
          <div
            id={`${label.replace(/\s+/g, '-').toLowerCase()}-options`}
            className="absolute z-[9999] mt-1 max-h-64 w-full overflow-y-auto rounded-lg border border-[#dfe6ff] bg-white py-1 shadow-lg"
            role="listbox"
          >
            <button
              type="button"
              className="w-full px-3 py-2 text-left text-sm text-parchment-200/70 hover:bg-parchment-50/5"
              onMouseDown={(event) => event.preventDefault()}
              onClick={() => {
                onSelect('')
                setSearch('')
                setOpen(false)
              }}
            >
              Manual inputs
            </button>
            {filteredProjects.map((project) => (
              <button
                key={project.id}
                type="button"
                role="option"
                aria-selected={String(project.id) === selected}
                className="block w-full px-3 py-2 text-left text-sm text-parchment-50 hover:bg-parchment-50/5"
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => {
                  onSelect(String(project.id))
                  setSearch('')
                  setOpen(false)
                }}
              >
                {project.project_name}
              </button>
            ))}
            {!filteredProjects.length && (
              <p className="px-3 py-2 text-sm text-parchment-200/60">No projects match that search.</p>
            )}
          </div>
        )}
      </div>
    </Field>
  )
}
