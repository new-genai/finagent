'use client';

import { useDatasetStats } from '@/hooks/useQueries';
import StatCard from '@/components/dashboard/StatCard';
import { Database, FileText, Building2, Calendar, Loader2 } from 'lucide-react';

export default function DashboardPage() {
  const { data: stats, isLoading, error } = useDatasetStats();

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] gap-4">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-muted-foreground animate-pulse">Loading analytics from backend...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-destructive p-8 text-center bg-destructive/10 rounded-xl max-w-2xl mx-auto mt-16 border border-destructive/20 shadow-sm">
        <h3 className="font-semibold text-lg mb-2">Connection Error</h3>
        <p>Could not load statistics. Ensure the FastAPI backend is running on port 8000.</p>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-10">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Database Overview</h1>
        <p className="text-muted-foreground">Monitor the extracted financial reports and DuckDB status.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard 
          title="Total Reports" 
          value={stats?.total_files || 0} 
          icon={FileText} 
          description="Processed TXT files" 
        />
        <StatCard 
          title="Extracted Tables" 
          value={stats?.total_tables || 0} 
          icon={Database} 
          description="Indexed in DuckDB & FAISS" 
        />
        <StatCard 
          title="Companies" 
          value={stats?.companies.length || 0} 
          icon={Building2} 
          description={stats?.companies.join(', ') || 'N/A'} 
        />
        <StatCard 
          title="Years Covered" 
          value={stats?.years.length || 0} 
          icon={Calendar} 
          description={stats?.years.join(', ') || 'N/A'} 
        />
      </div>
    </div>
  );
}
