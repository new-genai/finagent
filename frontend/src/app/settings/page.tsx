"use client"

import React from "react"
import { useTheme } from "next-themes"
import { Check, Monitor, Moon, Settings, Sun } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useDatasetStats, useHealthCheck } from "@/hooks/useQueries"
import { cn } from "@/lib/utils"

const themeOptions = [
  { value: "light", label: "Light", desc: "Giao diện sáng", icon: Sun },
  { value: "dark", label: "Dark", desc: "Giao diện tối", icon: Moon },
  { value: "system", label: "System", desc: "Theo hệ điều hành", icon: Monitor },
]

export default function SettingsPage() {
  const { theme, resolvedTheme, setTheme } = useTheme()
  const { data: health } = useHealthCheck()
  const { data: stats } = useDatasetStats()

  return (
    <div className="w-full space-y-5 py-2">
      <section className="border border-border bg-card p-5">
        <Badge variant="outline" className="rounded-none border-primary/40 text-primary">
          Preferences
        </Badge>
        <div className="mt-3 flex flex-col gap-2">
          <h1 className="text-3xl font-semibold tracking-normal">Settings</h1>
          <p className="max-w-2xl text-sm leading-6 text-muted-foreground">
            Quản lý giao diện, chế độ sáng tối và trạng thái dữ liệu của workspace.
          </p>
        </div>
      </section>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_360px]">
        <Card className="rounded-none border-border bg-card">
          <CardHeader className="border-b border-border">
            <CardTitle className="flex items-center gap-2 text-base">
              <Settings className="h-4 w-4 text-primary" />
              Theme
            </CardTitle>
            <CardDescription>Chọn chế độ giao diện bạn muốn dùng.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3 pt-4 md:grid-cols-3">
            {themeOptions.map((option) => {
              const Icon = option.icon
              const active = theme === option.value
              return (
                <button
                  key={option.value}
                  onClick={() => setTheme(option.value)}
                  className={cn(
                    "flex min-h-32 flex-col items-start justify-between border p-4 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                    active
                      ? "border-primary/40 bg-primary/10"
                      : "border-border bg-background hover:bg-secondary",
                  )}
                >
                  <div className="flex w-full items-center justify-between">
                    <Icon className="h-5 w-5 text-primary" />
                    {active && <Check className="h-4 w-4 text-primary" />}
                  </div>
                  <div>
                    <div className="font-semibold">{option.label}</div>
                    <div className="mt-1 text-sm text-muted-foreground">{option.desc}</div>
                  </div>
                </button>
              )
            })}
          </CardContent>
        </Card>

        <Card className="rounded-none border-border bg-card">
          <CardHeader className="border-b border-border">
            <CardTitle className="text-base">Runtime</CardTitle>
            <CardDescription>Trạng thái hiện tại của frontend và backend.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 pt-4 text-sm">
            <StatusRow label="Resolved theme" value={resolvedTheme ?? "loading"} />
            <StatusRow label="Backend" value={health?.status ?? "unknown"} />
            <StatusRow label="Reports" value={String(stats?.total_files ?? 0)} />
            <StatusRow label="Tables" value={String(stats?.total_tables ?? 0)} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function StatusRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border border-border bg-background px-3 py-2">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-mono font-medium">{value}</span>
    </div>
  )
}
