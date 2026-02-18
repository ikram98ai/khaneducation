import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "group relative inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0 active:scale-[0.98]",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary-hover shadow-medium hover:shadow-elevated hover:scale-[1.02] ease-out",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90 shadow-medium hover:shadow-large",
        outline: "border border-input bg-surface-base hover:bg-surface-hover hover:text-accent-foreground shadow-soft hover:shadow-medium backdrop-blur-subtle",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80 shadow-soft hover:shadow-medium",
        ghost: "hover:bg-surface-hover hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
        gradient: "bg-gradient-primary text-white hover:scale-105 hover:shadow-floating animate-pulse-glow",
        success: "bg-success text-success-foreground hover:bg-success/90 shadow-medium hover:shadow-large",
        warning: "bg-warning text-warning-foreground hover:bg-warning/90 shadow-medium hover:shadow-large",
        info: "bg-info text-info-foreground hover:bg-info/90 shadow-medium hover:shadow-large",
        course: "bg-surface-base text-card-foreground border border-glass hover:shadow-elevated hover:scale-[1.02] hover:bg-surface-hover backdrop-blur-subtle",
        glass: "bg-glass text-foreground border border-glass hover:bg-surface-hover shadow-medium hover:shadow-elevated backdrop-blur-glass",
        floating: "bg-surface-elevated text-foreground shadow-floating hover:shadow-floating hover:scale-[1.02] animate-float border border-glass/50 backdrop-blur-glass",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3 text-xs",
        lg: "h-12 rounded-lg px-8 text-base",
        xl: "h-14 rounded-lg px-10 text-lg",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
