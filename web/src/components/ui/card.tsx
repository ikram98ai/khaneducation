import * as React from "react"

import { cn } from "@/lib/utils"

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    variant?: 'default' | 'elevated' | 'glass' | 'floating' | 'interactive'
  }
>(({ className, variant = 'default', ...props }, ref) => {
  const variants = {
    default: "rounded-lg border bg-surface-base text-card-foreground shadow-soft hover:shadow-medium transition-all duration-300",
    elevated: "rounded-lg border bg-surface-elevated text-card-foreground shadow-elevated hover:shadow-floating transition-all duration-300 hover:scale-[1.01]",
    glass: "rounded-lg border border-glass bg-glass text-card-foreground shadow-medium backdrop-blur-glass hover:shadow-elevated transition-all duration-300",
    floating: "rounded-lg border border-glass/50 bg-surface-glass text-card-foreground shadow-floating backdrop-blur-glass animate-float hover:shadow-floating hover:scale-[1.02] transition-all duration-300",
    interactive: "rounded-lg border bg-surface-base text-card-foreground shadow-soft hover:shadow-elevated hover:scale-[1.02] hover:bg-surface-hover cursor-pointer transition-all duration-300 active:scale-[0.98]"
  }
  
  return (
    <div
      ref={ref}
      className={cn(variants[variant], className)}
      {...props}
    />
  )
})
Card.displayName = "Card"

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-2xl font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
