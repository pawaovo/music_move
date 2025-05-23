// @ts-nocheck
import * as React from "react"

import { cn } from "@/lib/utils"

export const Card = ({
  className = '',
  children,
  ...props
}) => {
  return (
    <div
      className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

export const CardHeader = ({
  className = '',
  children,
  ...props
}) => {
  return (
    <div
      className={`flex flex-col space-y-1.5 p-6 ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

export const CardTitle = ({
  className = '',
  children,
  ...props
}) => {
  return (
    <h3
      className={`text-2xl font-semibold leading-none tracking-tight ${className}`}
      {...props}
    >
      {children}
    </h3>
  )
}

export const CardDescription = ({
  className = '',
  children,
  ...props
}) => {
  return (
    <p
      className={`text-sm text-muted-foreground ${className}`}
      {...props}
    >
      {children}
    </p>
  )
}

export const CardContent = ({
  className = '',
  children,
  ...props
}) => {
  return (
    <div
      className={`p-6 pt-0 ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

export const CardFooter = ({
  className = '',
  children,
  ...props
}) => {
  return (
    <div
      className={`flex items-center p-6 pt-0 ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}
