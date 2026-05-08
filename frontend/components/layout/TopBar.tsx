"use client";

import { useEffect, useRef, useState } from "react";
import { useAppContext } from "@/lib/context";
import { stripEmoji } from "@/lib/utils";
import { ChevronDown } from "lucide-react";
import WalletBalanceChip from "@/components/cockpit/WalletBalanceChip";
import WalletManagementDrawer from "@/components/cockpit/WalletManagementDrawer";
import { fetchBalances } from "@/lib/cockpit/finances-api";

export default function TopBar() {
    const { formats, activeFormat, switchFormat } = useAppContext();
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [walletBalance, setWalletBalance] = useState(0);
    const [isMounted, setIsMounted] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const timer = window.setTimeout(() => {
            setIsMounted(true);
        }, 0);
        return () => window.clearTimeout(timer);
    }, []);

    useEffect(() => {
        let cancelled = false;
        function refresh() {
            fetchBalances()
                .then((b) => { if (!cancelled) setWalletBalance(b.wallet); })
                .catch(() => {});
        }
        refresh();
        const interval = setInterval(refresh, 15000);
        return () => {
            cancelled = true;
            clearInterval(interval);
        };
    }, []);

    const activeFmt = formats.find((f) => f.key === activeFormat);
    const formatLabel = activeFmt ? stripEmoji(activeFmt.label).trim() : "";

    useEffect(() => {
        if (!dropdownOpen) return;
        function handleClickOutside(e: MouseEvent) {
            if (
                dropdownRef.current &&
                !dropdownRef.current.contains(e.target as Node)
            ) {
                setDropdownOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () =>
            document.removeEventListener("mousedown", handleClickOutside);
    }, [dropdownOpen]);

    return (
        <>
        <header className="topbar" role="banner">
            <div className="topbar-wordmark">
                <span className="topbar-title">VANTAGE</span>
            </div>

            {isMounted && (
                <div className="topbar-right-group">
                <WalletBalanceChip
                    balance={walletBalance}
                    onOpenDrawer={() => setDrawerOpen(true)}
                />
                <div className="format-switcher" ref={dropdownRef}>
                    <button
                        type="button"
                        className="format-switcher-trigger"
                        onClick={() => setDropdownOpen((prev) => !prev)}
                        aria-label={`Active format: ${formatLabel || "None"}. Click to switch format.`}
                        aria-expanded={dropdownOpen}
                        aria-haspopup="listbox"
                    >
                        <span className="format-switcher-label">
                            Format: {formatLabel || "Select"}
                        </span>
                        <ChevronDown
                            size={14}
                            className={`format-switcher-chevron ${dropdownOpen ? "open" : ""}`}
                        />
                    </button>

                    {dropdownOpen && (
                        <ul
                            className="format-switcher-menu"
                            role="listbox"
                            aria-label="Select format"
                        >
                            {formats.map((fmt) => {
                                const label = stripEmoji(fmt.label).trim();
                                const isActive =
                                    isMounted && fmt.key === activeFormat;
                                return (
                                    <li
                                        key={fmt.key}
                                        role="option"
                                        aria-selected={isActive}
                                        className={`format-switcher-item ${isActive ? "active" : ""} ${!fmt.has_manifest ? "disabled" : ""}`}
                                        onClick={() => {
                                            if (!fmt.has_manifest) return;
                                            switchFormat(fmt.key);
                                            setDropdownOpen(false);
                                        }}
                                        onKeyDown={(e) => {
                                            if (
                                                e.key === "Enter" ||
                                                e.key === " "
                                            ) {
                                                e.preventDefault();
                                                if (!fmt.has_manifest) return;
                                                switchFormat(fmt.key);
                                                setDropdownOpen(false);
                                            }
                                        }}
                                        tabIndex={fmt.has_manifest ? 0 : -1}
                                    >
                                        {label}
                                        {!fmt.has_manifest && (
                                            <span className="format-switcher-soon">
                                                Soon
                                            </span>
                                        )}
                                    </li>
                                );
                            })}
                        </ul>
                    )}
                </div>
                </div>
            )}
        </header>
        <WalletManagementDrawer
            isOpen={drawerOpen}
            onClose={() => setDrawerOpen(false)}
            onBalanceChange={(w) => setWalletBalance(w)}
        />
        </>
    );
}
