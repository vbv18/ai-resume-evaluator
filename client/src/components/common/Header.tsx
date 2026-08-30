import React from "react";
import { Link, useLocation } from "react-router-dom";
import { ThemeToggle } from "./ThemeToggle";
import { FileText, Briefcase, Sparkles, LayoutDashboard, UserCheck } from "lucide-react";
import { cn } from "../../lib/utils";

interface HeaderProps {
  userEmail?: string;
}

export const Header: React.FC<HeaderProps> = ({ userEmail = "alex.johnson@example.com" }) => {
  const location = useLocation();

  const navItems = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Resumes", href: "/resumes", icon: FileText },
    { name: "Job Catalog", href: "/jobs", icon: Briefcase },
    { name: "Evaluate", href: "/evaluate", icon: Sparkles },
    { name: "History", href: "/history", icon: UserCheck },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/60 bg-background/85 backdrop-blur-md transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-8">
          <Link to="/" className="flex items-center space-x-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary group-hover:scale-105 transition-transform">
              <Sparkles className="w-4 h-4" />
            </div>
            <div className="flex flex-col">
              <span className="font-semibold text-sm tracking-tight text-foreground">
                ResumeFit AI
              </span>
              <span className="text-[10px] text-muted-foreground tracking-wider uppercase">
                Evaluator & Optimizer
              </span>
            </div>
          </Link>

          {/* Nav Items */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive =
                item.href === "/"
                  ? location.pathname === "/"
                  : location.pathname.startsWith(item.href);

              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    "flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors",
                    isActive
                      ? "bg-muted text-foreground font-semibold shadow-xs"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                  )}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right Section */}
        <div className="flex items-center space-x-4">
          <ThemeToggle />

          <div className="flex items-center space-x-2 pl-2 border-l border-border/60">
            <div className="w-7 h-7 rounded-full bg-primary/20 text-primary border border-primary/30 flex items-center justify-center text-xs font-semibold">
              {userEmail.charAt(0).toUpperCase()}
            </div>
            <span className="hidden sm:inline-block text-xs font-medium text-muted-foreground truncate max-w-[120px]">
              {userEmail.split("@")[0]}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
