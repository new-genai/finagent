import Link from "next/link"
import { MapPinOff } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function NotFound() {
  return (
    <div className="flex h-full w-full flex-col items-center justify-center gap-6 p-8 bg-background text-center">
      <div className="flex h-20 w-20 items-center justify-center rounded-full bg-muted">
        <MapPinOff className="h-10 w-10 text-muted-foreground" />
      </div>
      <div className="space-y-2 max-w-md">
        <h2 className="text-2xl font-bold tracking-tight">404 - Page Not Found</h2>
        <p className="text-muted-foreground">
          The module or page you are looking for does not exist in this version of NewGenAI Financial Agent.
        </p>
      </div>
      <Link href="/">
        <Button>Return to Dashboard</Button>
      </Link>
    </div>
  )
}
