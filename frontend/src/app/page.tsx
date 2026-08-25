"use client"

import React, { useMemo, useState } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import {
  ArrowRight,
  BarChart2,
  Database,
  FileText,
  MessageSquare,
  Search,
  Table2,
} from "lucide-react"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useDatasetStats } from "@/hooks/useQueries"

const chartColors = [
  "oklch(0.62 0.18 248)",
  "oklch(0.66 0.17 178)",
  "oklch(0.72 0.16 82)",
  "oklch(0.64 0.18 22)",
  "oklch(0.66 0.15 305)",
  "oklch(0.58 0.13 145)",
]

const formatNumber = (value: number) => new Intl.NumberFormat("en-US").format(value)

export default function DashboardPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const { data: stats, isLoading } = useDatasetStats()
  const router = useRouter()

  const companyCounts = useMemo(() => stats?.company_table_counts ?? {}, [stats?.company_table_counts])
  const yearCounts = useMemo(() => stats?.year_table_counts ?? {}, [stats?.year_table_counts])
  const totalFiles = stats?.total_files ?? 0
  const totalTables = stats?.total_tables ?? 0
  const companies = stats?.companies ?? []
  const years = stats?.years ?? []

  const companyChartData = useMemo(() => {
    const sorted = Object.entries(companyCounts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
    const top = sorted.slice(0, 8)
    const other = sorted.slice(8).reduce((sum, item) => sum + item.value, 0)
    return other ? [...top, { name: "Other", value: other }] : top
  }, [companyCounts])

  const yearChartData = useMemo(
    () => Object.entries(yearCounts).map(([name, value]) => ({ name, value })),
    [yearCounts],
  )

  const metricRows = [
    {
      label: "Reports indexed",
      value: totalFiles,
      unit: "company-years",
      detail: "Distinct ticker/year pairs parsed from real table names",
    },
    {
      label: "Extracted tables",
      value: totalTables,
      unit: "tables",
      detail: "Actual DuckDB tables available to retrieval and execution",
    },
    {
      label: "Companies",
      value: companies.length,
      unit: "tickers",
      detail: companies.slice(0, 12).join(", ") || "No company metadata returned",
    },
    {
      label: "Years covered",
      value: years.length,
      unit: "years",
      detail: years.join(", ") || "No reporting years returned",
    },
  ]

  const actions = [
    { name: "Chat", desc: "Ask over financial tables", icon: MessageSquare, href: "/chat" },
    { name: "Dataset", desc: `${formatNumber(totalTables)} real tables`, icon: Database, href: "/dataset" },
    { name: "Parser", desc: "Extract new reports", icon: FileText, href: "/parser" },
    { name: "Evaluation", desc: "Measure retrieval quality", icon: BarChart2, href: "/evaluation" },
  ]

  const handleSearch = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter" && searchQuery.trim()) {
      router.push("/chat")
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className="w-full space-y-5 py-2"
    >
      <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_420px]">
        <motion.div layout className="border border-border bg-card p-5">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div className="space-y-3">
              <Badge variant="outline" className="rounded-none border-primary/40 text-primary">
                Live DuckDB dashboard
              </Badge>
              <div className="space-y-2">
                <h1 className="text-3xl font-semibold tracking-normal md:text-4xl">Dashboard</h1>
                <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
                  Theo dõi dữ liệu thật từ DuckDB: số bảng, mã công ty, năm báo cáo và phân bổ nguồn dữ liệu.
                </p>
              </div>
            </div>

            <div className="flex min-w-0 items-center border-2 border-border bg-background focus-within:border-primary lg:w-[380px]">
              <div className="px-4 text-muted-foreground">
                <Search className="h-5 w-5" />
              </div>
              <input
                suppressHydrationWarning
                type="text"
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                onKeyDown={handleSearch}
                placeholder="Query financial data..."
                className="min-w-0 flex-1 border-none bg-transparent py-4 text-sm text-foreground outline-none placeholder:text-muted-foreground"
              />
            </div>
          </div>

          <div className="mt-5 grid grid-cols-2 gap-px bg-border md:grid-cols-4">
            {metricRows.map((row, index) => (
              <motion.div
                key={row.label}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.04, duration: 0.28 }}
                className="bg-card p-4"
              >
                <div className="font-mono text-2xl font-semibold tabular-nums">
                  {isLoading ? "--" : formatNumber(row.value)}
                </div>
                <div className="mt-1 text-xs text-muted-foreground">{row.unit}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        <ChartCard
          title="Company Distribution"
          description="Số bảng thật theo mã công ty."
          icon={<Table2 className="h-4 w-4 text-primary" />}
        >
          {companyChartData.length ? (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Tooltip formatter={(value) => formatNumber(Number(value))} />
                <Pie data={companyChartData} dataKey="value" nameKey="name" innerRadius={58} outerRadius={92} paddingAngle={2}>
                  {companyChartData.map((entry, index) => (
                    <Cell key={entry.name} fill={chartColors[index % chartColors.length]} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState label="No company data returned" />
          )}
        </ChartCard>
      </section>

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1.15fr)_minmax(360px,0.85fr)]">
        <Card className="rounded-none border-border bg-card">
          <CardHeader className="border-b border-border">
            <div className="flex items-center justify-between gap-3">
              <div>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Database className="h-4 w-4 text-primary" />
                  Source Inventory
                </CardTitle>
                <CardDescription>Bảng kiểm kê đọc từ thống kê backend hiện tại.</CardDescription>
              </div>
              <Badge variant="secondary" className="rounded-none">
                Real data
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead className="h-12 px-4">Metric</TableHead>
                  <TableHead className="h-12 px-4 text-right">Value</TableHead>
                  <TableHead className="h-12 px-4">Unit</TableHead>
                  <TableHead className="h-12 px-4">Detail</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {metricRows.map((row) => (
                  <TableRow key={row.label}>
                    <TableCell className="px-4 font-medium">{row.label}</TableCell>
                    <TableCell className="px-4 text-right font-mono text-base tabular-nums">
                      {isLoading ? "--" : formatNumber(row.value)}
                    </TableCell>
                    <TableCell className="px-4 text-muted-foreground">{row.unit}</TableCell>
                    <TableCell className="max-w-[460px] px-4 text-muted-foreground">
                      <span className="line-clamp-2 whitespace-normal">{row.detail}</span>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <ChartCard
          title="Year Coverage"
          description="Số bảng thật theo năm báo cáo."
          icon={<BarChart2 className="h-4 w-4 text-primary" />}
        >
          {yearChartData.length ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={yearChartData} margin={{ top: 10, right: 8, left: -18, bottom: 0 }}>
                <CartesianGrid stroke="var(--border)" vertical={false} />
                <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fill: "currentColor", fontSize: 11 }} />
                <YAxis tickLine={false} axisLine={false} tick={{ fill: "currentColor", fontSize: 11 }} allowDecimals={false} />
                <Tooltip formatter={(value) => formatNumber(Number(value))} cursor={{ fill: "var(--secondary)" }} />
                <Bar dataKey="value" radius={[0, 0, 0, 0]}>
                  {yearChartData.map((entry, index) => (
                    <Cell key={entry.name} fill={chartColors[index % chartColors.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState label="No year data returned" />
          )}
        </ChartCard>
      </section>

      <section className="grid gap-4 lg:grid-cols-4">
        {actions.map((action, index) => (
          <motion.button
            key={action.name}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.16 + index * 0.04, duration: 0.28 }}
            onClick={() => router.push(action.href)}
            className="group flex min-h-28 flex-col items-start justify-between border border-border bg-card p-4 text-left transition-colors hover:border-primary hover:bg-secondary/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <div className="flex w-full items-center justify-between gap-3">
              <action.icon className="h-5 w-5 text-muted-foreground group-hover:text-primary" />
              <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
            </div>
            <div>
              <div className="font-semibold">{action.name}</div>
              <div className="mt-1 text-sm text-muted-foreground">{action.desc}</div>
            </div>
          </motion.button>
        ))}
      </section>
    </motion.div>
  )
}

function ChartCard({
  title,
  description,
  icon,
  children,
}: {
  title: string
  description: string
  icon: React.ReactNode
  children: React.ReactNode
}) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.32 }}>
      <Card className="rounded-none border-border bg-card">
        <CardHeader className="border-b border-border">
          <CardTitle className="flex items-center gap-2 text-base">
            {icon}
            {title}
          </CardTitle>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent className="h-[302px] pt-4">{children}</CardContent>
      </Card>
    </motion.div>
  )
}

function EmptyState({ label }: { label: string }) {
  return (
    <div className="flex h-full items-center justify-center border border-dashed border-border text-sm text-muted-foreground">
      {label}
    </div>
  )
}
