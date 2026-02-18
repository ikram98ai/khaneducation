import { ChevronRight, Home } from "lucide-react";
import { Button } from "@/components/ui/button";

interface BreadcrumbItem {
  label: string;
  onClick?: () => void;
  isActive?: boolean;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export const Breadcrumb = ({ items }: BreadcrumbProps) => {
  return (
    <nav className="flex items-center space-x-2 text-sm animate-slide-up-fade">
      <Button
        variant="ghost"
        size="sm"
        onClick={items[0]?.onClick}
        className="p-1 h-8 w-8"
      >
        <Home className="h-4 w-4" />
      </Button>
      
      {items.map((item, index) => (
        <div key={index} className="flex items-center space-x-2">
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
          <Button
            variant="ghost"
            size="sm"
            onClick={item.onClick}
            disabled={item.isActive}
            className={`text-sm h-8 px-2 ${
              item.isActive 
                ? 'text-foreground font-medium cursor-default' 
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {item.label}
          </Button>
        </div>
      ))}
    </nav>
  );
};