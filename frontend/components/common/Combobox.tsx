"use client";

import {
  useEffect,
  useId,
  useRef,
  useState,
  useMemo,
  type KeyboardEvent,
  type MouseEvent,
} from "react";

export interface ComboboxOption {
  label: string;
  value: string;
}

interface ComboboxProps {
  value: string;
  onChange: (value: string) => void;
  options: ComboboxOption[];
  placeholder?: string;
  label?: string;
  error?: string;
  disabled?: boolean;
}

export function Combobox({
  value,
  onChange,
  options,
  placeholder,
  label,
  error,
  disabled = false,
}: ComboboxProps) {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const listboxId = useId();
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [searchQuery, setSearchQuery] = useState("");

  const selectedLabel = options.find((o) => o.value === value)?.label ?? "";

  const filteredOptions = useMemo(() => {
    if (!searchQuery.trim()) return options;
    const q = searchQuery.toLowerCase();
    return options.filter((o) => o.label.toLowerCase().includes(q));
  }, [options, searchQuery]);

  useEffect(() => {
    if (isOpen) setActiveIndex(filteredOptions.length > 0 ? 0 : -1);
  }, [filteredOptions, isOpen]);

  useEffect(() => {
    const handleDocumentMouseDown = (e: globalThis.MouseEvent): void => {
      if (!(e.target instanceof Node) || !rootRef.current?.contains(e.target)) {
        setIsOpen(false);
        setSearchQuery("");
      }
    };
    document.addEventListener("mousedown", handleDocumentMouseDown);
    return () => document.removeEventListener("mousedown", handleDocumentMouseDown);
  }, []);

  const openList = (): void => {
    setIsOpen(true);
    setSearchQuery("");
    setActiveIndex(0);
  };

  const selectOption = (option: ComboboxOption): void => {
    onChange(option.value);
    setIsOpen(false);
    setSearchQuery("");
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>): void => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (!isOpen) { openList(); return; }
      setActiveIndex((i) => Math.min(i < 0 ? 0 : i + 1, filteredOptions.length - 1));
      return;
    }
    if (e.key === "ArrowUp") {
      e.preventDefault();
      if (!isOpen) { openList(); return; }
      setActiveIndex((i) => Math.max(i < 0 ? filteredOptions.length - 1 : i - 1, 0));
      return;
    }
    if (e.key === "Enter" && isOpen) {
      e.preventDefault();
      const target = filteredOptions[activeIndex >= 0 ? activeIndex : 0];
      if (target) selectOption(target);
      return;
    }
    if (e.key === "Escape" || e.key === "Tab") {
      setIsOpen(false);
      setSearchQuery("");
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchQuery(e.target.value);
    if (!isOpen) setIsOpen(true);
  };

  const handleInputClick = (): void => {
    if (isOpen) { setIsOpen(false); setSearchQuery(""); return; }
    openList();
  };

  const handleOptionMouseDown = (e: MouseEvent<HTMLLIElement>): void => {
    e.preventDefault();
  };

  const errorClass = error ? "context-input-error" : "";
  const activeDescendant = isOpen && activeIndex >= 0 ? `${listboxId}-option-${activeIndex}` : undefined;
  const displayValue = isOpen ? searchQuery : selectedLabel;

  return (
    <div>
      {label && <label className="input-label">{label}</label>}
      <div ref={rootRef} className="relative">
        <input
          ref={inputRef}
          type="text"
          role="combobox"
          aria-expanded={isOpen}
          aria-autocomplete="list"
          aria-controls={listboxId}
          aria-activedescendant={activeDescendant}
          className={`context-input ${errorClass}`.trim()}
          value={displayValue}
          placeholder={placeholder}
          disabled={disabled}
          onClick={handleInputClick}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
        />
        {isOpen && (
          <ul
            id={listboxId}
            role="listbox"
            className="combobox-listbox"
          >
            {filteredOptions.length === 0 ? (
              <li className="combobox-option-empty">No matches found</li>
            ) : (
              filteredOptions.map((option, index) => {
                const isActive = index === activeIndex;
                const isSelected = option.value === value;
                return (
                  <li
                    key={option.value}
                    id={`${listboxId}-option-${index}`}
                    role="option"
                    aria-selected={isSelected}
                    className={isActive ? "combobox-option combobox-option-active" : "combobox-option"}
                    onMouseDown={handleOptionMouseDown}
                    onClick={() => selectOption(option)}
                  >
                    {option.label}
                  </li>
                );
              })
            )}
          </ul>
        )}
      </div>
      {error && <p className="input-error-text">{error}</p>}
    </div>
  );
}
