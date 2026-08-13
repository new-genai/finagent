import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "@/providers/theme-provider";
import { QueryProvider } from "@/providers/query-provider";
import { AppLayout } from "@/components/layout/AppLayout";
import { Toaster } from "sonner";

export const metadata: Metadata = {
  title: "NewGenAI Financial Agent",
  description: "AI-powered financial data analysis platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        suppressHydrationWarning
        className="antialiased font-sans h-screen w-screen overflow-hidden"
      >
        <QueryProvider>
          <ThemeProvider
            attribute="class"
            defaultTheme="dark"
            forcedTheme="dark"
            disableTransitionOnChange
          >
            <AppLayout>{children}</AppLayout>
            <Toaster richColors position="top-right" theme="dark" />
          </ThemeProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
