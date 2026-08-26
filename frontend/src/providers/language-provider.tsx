"use client"

import React, { createContext, useContext, useState, useEffect } from "react"

type Language = "EN" | "VI"

interface LanguageContextType {
  lang: Language
  setLang: (lang: Language) => void
  toggleLang: () => void
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined)

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Language>("EN")
  const [mounted, setMounted] = useState(false)

  // Load from localStorage if available
  useEffect(() => {
    const savedLang = localStorage.getItem("finagent-lang") as Language
    if (savedLang === "VI" || savedLang === "EN") {
      setLangState(savedLang)
    }
    setMounted(true)
  }, [])

  const setLang = (newLang: Language) => {
    setLangState(newLang)
    localStorage.setItem("finagent-lang", newLang)
  }

  const toggleLang = () => {
    setLang(lang === "EN" ? "VI" : "EN")
  }

  // Prevents hydration mismatch for text that changes based on lang
  if (!mounted) {
    return <div style={{ visibility: "hidden" }}>{children}</div>
  }

  return (
    <LanguageContext.Provider value={{ lang, setLang, toggleLang }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  const context = useContext(LanguageContext)
  if (context === undefined) {
    throw new Error("useLanguage must be used within a LanguageProvider")
  }
  return context
}
