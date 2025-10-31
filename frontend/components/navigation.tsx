"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Settings,
  TestTube2,
  PlayCircle,
  Github,
  MessageSquare,
  Menu,
  Library,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const navItems = [
  {
    name: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    name: "Test Library",
    href: "/test-library",
    icon: Library,
  },
  {
    name: "Test Configuration",
    href: "/test-config",
    icon: TestTube2,
  },
  {
    name: "Settings",
    href: "/settings",
    icon: Settings,
  },
];

export function Navigation() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 justify-between">
          <div className="flex">
            {/* Logo */}
            <div className="flex flex-shrink-0 items-center">
              <Link href="/" className="flex items-center gap-2">
                <TestTube2 className="h-8 w-8 text-orange-500" />
                <span className="text-xl font-bold text-gray-900">
                  TestGPT
                </span>
              </Link>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {navItems.map((item) => {
                if (item.submenu) {
                  return (
                    <div key={item.name} className="relative flex items-center">
                      <div className="group relative">
                        <button className="inline-flex items-center gap-2 border-b-2 border-transparent px-1 pt-1 text-sm font-medium text-gray-500 hover:border-gray-300 hover:text-gray-700">
                          <item.icon className="h-4 w-4" />
                          {item.name}
                        </button>
                        <div className="absolute left-0 mt-2 hidden w-48 rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 group-hover:block">
                          <div className="py-1">
                            {item.submenu.map((subitem) => {
                              const isActive = pathname === subitem.href;
                              return (
                                <Link
                                  key={subitem.href}
                                  href={subitem.href}
                                  className={cn(
                                    "flex items-center gap-2 px-4 py-2 text-sm",
                                    isActive
                                      ? "bg-gray-100 text-gray-900"
                                      : "text-gray-700 hover:bg-gray-50"
                                  )}
                                >
                                  <subitem.icon className="h-4 w-4" />
                                  {subitem.name}
                                </Link>
                              );
                            })}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                }

                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "inline-flex items-center gap-2 border-b-2 px-1 pt-1 text-sm font-medium",
                      isActive
                        ? "border-orange-500 text-gray-900"
                        : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
                    )}
                  >
                    <item.icon className="h-4 w-4" />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="flex items-center sm:hidden">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              <Menu className="h-6 w-6" />
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="sm:hidden">
          <div className="space-y-1 pb-3 pt-2">
            {navItems.map((item) => {
              if (item.submenu) {
                return (
                  <div key={item.name}>
                    <div className="flex items-center gap-2 px-4 py-2 text-base font-medium text-gray-500">
                      <item.icon className="h-5 w-5" />
                      {item.name}
                    </div>
                    {item.submenu.map((subitem) => {
                      const isActive = pathname === subitem.href;
                      return (
                        <Link
                          key={subitem.href}
                          href={subitem.href}
                          className={cn(
                            "flex items-center gap-2 py-2 pl-8 pr-4 text-base font-medium",
                            isActive
                              ? "border-l-4 border-orange-500 bg-orange-50 text-orange-700"
                              : "border-l-4 border-transparent text-gray-500 hover:border-gray-300 hover:bg-gray-50 hover:text-gray-700"
                          )}
                          onClick={() => setMobileMenuOpen(false)}
                        >
                          <subitem.icon className="h-5 w-5" />
                          {subitem.name}
                        </Link>
                      );
                    })}
                  </div>
                );
              }

              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2 border-l-4 py-2 pl-4 pr-4 text-base font-medium",
                    isActive
                      ? "border-orange-500 bg-orange-50 text-orange-700"
                      : "border-transparent text-gray-500 hover:border-gray-300 hover:bg-gray-50 hover:text-gray-700"
                  )}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <item.icon className="h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </nav>
  );
}
