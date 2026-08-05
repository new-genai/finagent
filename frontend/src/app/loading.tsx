export default function Loading() {
  return (
    <div className="flex h-full w-full items-center justify-center p-8 bg-background">
      <div className="flex flex-col items-center gap-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        <p className="text-sm text-muted-foreground animate-pulse">Loading platform...</p>
      </div>
    </div>
  )
}
