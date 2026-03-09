"use client";

import { useEffect, useId, useRef, useState, useMemo, type KeyboardEvent, type MouseEvent } from "react";

interface ComboboxOption {
  label: string;
  value: string;
}

interface AccessibleComboboxProps {
  value: string;
  onChange: (value: string) => void;
  options: ComboboxOption[];
  placeholder?: string;
}

function AccessibleCombobox({
  value,
  onChange,
  options,
  placeholder,
}: AccessibleComboboxProps) {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const listboxId = useId();
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [activeIndex, setActiveIndex] = useState<number>(-1);
  const [searchQuery, setSearchQuery] = useState<string>("");

  const selectedOption = options.find((option) => option.value === value);
  const selectedLabel = selectedOption ? selectedOption.label : "";

  // Filter options based on search query
  const filteredOptions = useMemo(() => {
    if (!searchQuery.trim()) {
      return options;
    }
    const query = searchQuery.toLowerCase();
    return options.filter(
      (option) => option.label.toLowerCase().includes(query)
    );
  }, [options, searchQuery]);

  // Reset active index when filtered options change
  useEffect(() => {
    if (isOpen) {
      setActiveIndex(filteredOptions.length > 0 ? 0 : -1);
    }
  }, [filteredOptions, isOpen]);

  useEffect(() => {
    const handleDocumentMouseDown = (event: globalThis.MouseEvent): void => {
      if (!(event.target instanceof Node) || !rootRef.current?.contains(event.target)) {
        setIsOpen(false);
        // Reset search query to selected label when closing
        setSearchQuery("");
      }
    };

    document.addEventListener("mousedown", handleDocumentMouseDown);

    return () => {
      document.removeEventListener("mousedown", handleDocumentMouseDown);
    };
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

  const handleInputKeyDown = (event: KeyboardEvent<HTMLInputElement>): void => {
    if (event.key === "ArrowDown") {
      event.preventDefault();

      if (!isOpen) {
        openList();
        return;
      }

      setActiveIndex((currentIndex) => {
        const nextIndex = currentIndex < 0 ? 0 : Math.min(currentIndex + 1, filteredOptions.length - 1);
        return nextIndex;
      });
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();

      if (!isOpen) {
        openList();
        return;
      }

      setActiveIndex((currentIndex) => {
        const nextIndex = currentIndex < 0 ? filteredOptions.length - 1 : Math.max(currentIndex - 1, 0);
        return nextIndex;
      });
      return;
    }

    if (event.key === "Enter" && isOpen) {
      event.preventDefault();
      const target = filteredOptions[activeIndex >= 0 ? activeIndex : 0];
      if (target) {
        selectOption(target);
      }
      return;
    }

    if (event.key === "Escape") {
      setIsOpen(false);
      setSearchQuery("");
      return;
    }

    if (event.key === "Tab") {
      setIsOpen(false);
      setSearchQuery("");
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const query = e.target.value;
    setSearchQuery(query);
    if (!isOpen) {
      setIsOpen(true);
    }
  };

  const handleInputClick = (): void => {
    if (isOpen) {
      setIsOpen(false);
      setSearchQuery("");
      return;
    }
    openList();
  };

  const handleOptionMouseDown = (event: MouseEvent<HTMLLIElement>): void => {
    event.preventDefault();
  };

  // Display value: when open and typing, show query; otherwise show selected label
  const displayValue = isOpen ? searchQuery : selectedLabel;

  const activeDescendant = isOpen && activeIndex >= 0 ? `combobox-option-${activeIndex}` : undefined;

  return (
    <div ref={rootRef} className="[position:relative]">
      <input
        ref={inputRef}
        type="text"
        role="combobox"
        aria-expanded={isOpen}
        aria-autocomplete="list"
        aria-controls={listboxId}
        aria-activedescendant={activeDescendant}
        className="context-input"
        value={displayValue}
        placeholder={placeholder}
        onClick={handleInputClick}
        onChange={handleInputChange}
        onKeyDown={handleInputKeyDown}
      />

      {isOpen ? (
        <ul
          id={listboxId}
          role="listbox"
          className="[position:absolute] [top:calc(100%_+_var(--radius-sm))] [left:0] [right:0] [display:flex] [flex-direction:column] [gap:var(--radius-sm)] [margin:0] [padding:var(--radius-sm)] [list-style:none] [background:var(--bg-elevated)] [border:1px_solid_var(--border-default)] [border-radius:var(--radius-md)] [box-shadow:var(--shadow-md)] [z-index:50] [max-height:280px] [overflow-y:auto]"
        >
          {filteredOptions.length === 0 ? (
            <li className="[padding:var(--radius-md)] [color:var(--text-disabled)] [text-align:center] [font-size:0.85rem]">
              No matches found
            </li>
          ) : (
            filteredOptions.map((option, index) => {
              const isActive = index === activeIndex;
              const isSelected = option.value === value;

              return (
                <li
                  key={option.value}
                  id={`combobox-option-${index}`}
                  role="option"
                  aria-selected={isSelected}
                  className={
                    isActive
                      ? "[padding:var(--radius-md)] [border:1px_solid_var(--border-accent)] [border-radius:var(--radius-sm)] [background:var(--bg-hover)] [color:var(--text-primary)] [cursor:pointer]"
                      : "[padding:var(--radius-md)] [border:1px_solid_var(--bg-elevated)] [border-radius:var(--radius-sm)] [background:var(--bg-elevated)] [color:var(--text-secondary)] [cursor:pointer]"
                  }
                  onMouseDown={handleOptionMouseDown}
                  onClick={() => {
                    selectOption(option);
                  }}
                >
                  {option.label}
                </li>
              );
            })
          )}
        </ul>
      ) : null}
    </div>
  );
}

export { AccessibleCombobox };
