import { Bell, ChevronDown, LogOut, Settings, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuthStore } from "@/stores/authStore";

export function Navbar() {
  const { isAuthenticated, isLoading, profile } = useAuthStore();
  return (
    <header className="flex h-16 items-center justify-between px-4 md:px-6 max-w-6xl mx-auto bg-gradient-to-br from-background via-accent/5 to-primary/5">
      <div className="flex items-center gap-4">
        <a href="/dashboard" className="flex items-center gap-2">
          <img
            src="/logo.png"
            alt="khan education logo"
            className="h-16 w-16"
          />
          <span className="text-lg font-bold">Khan Education</span>
        </a>
      </div>

      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" className="rounded-full">
          <Bell className="h-6 w-6" />
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="flex items-center gap-2">
              <img
                src={profile.user.dp || "/placeholder.svg"}
                alt="Avatar"
                className="h-8 w-8 rounded-full"
              />
              <span className="hidden md:inline">
                {!isLoading && profile.user.username}
              </span>
              <ChevronDown className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuGroup>
              <a href="/profile"> 
              <DropdownMenuItem>
                <User className="mr-2 h-4 w-4" />
                <span> Profile </span>
              </DropdownMenuItem>
               </a> 
              <DropdownMenuItem>
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <LogOut className="mr-2 h-4 w-4" />
              <span onClick={useAuthStore.getState().clearAuth}>Logout</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
