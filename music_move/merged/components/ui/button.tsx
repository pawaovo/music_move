// @ts-nocheck
import * as React from "react"

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'outline' | 'ghost'
  size?: 'default' | 'sm' | 'lg'
  children: React.ReactNode
  className?: string
}

export const Button = ({
  variant = 'default',
  size = 'default',
  className = '',
  children,
  ...props
}) => {
  return (
    <button
      className={`inline-flex items-center justify-center rounded-md font-medium transition-colors ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}

export const buttonVariants = () => ""
