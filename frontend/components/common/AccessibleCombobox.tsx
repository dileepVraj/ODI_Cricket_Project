"use client";

import { useEffect, useId, useRef, useState, type KeyboardEvent, type MouseEvent } from "react";

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

  const selectedIndex = options.findIndex((option) => option.value === value);
  const selectedLabel = selectedIndex >= 0 ? options[selectedIndex].label : "";

  useEffect(() => {
    setActiveIndex(selectedIndex);
  }, [selectedIndex]);

  useEffect(() => {
    const handleDocumentMouseDown = (event: globalThis.MouseEvent): void => {
      if (!(event.target instanceof Node) || !rootRef.current?.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleDocumentMouseDown);

    return () => {
      document.removeEventListener("mousedown", handleDocumentMouseDown);
    };
  }, []);

  const openList = (index: number): void => {
    if (options.length === 0) {
      return;
    }

    setIsOpen(true);
    setActiveIndex(index);
  };

  const selectOption = (index: number): void => {
    const nextOption = options[index];

    if (!nextOption) {
      return;
    }

    onChange(nextOption.value);
    setActiveIndex(index);
    setIsOpen(false);
    inputRef.current?.focus();
  };

  const handleInputKeyDown = (event: KeyboardEvent<HTMLInputElement>): void => {
    if (options.length === 0) {
      if (event.key === "Escape" || event.key === "Tab") {
        setIsOpen(false);
      }
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();

      if (!isOpen) {
        openList(0);
        return;
      }

      setActiveIndex((currentIndex) => {
        const nextIndex = currentIndex < 0 ? 0 : Math.min(currentIndex + 1, options.length - 1);
        return nextIndex;
      });
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();

      if (!isOpen) {
        openList(selectedIndex >= 0 ? selectedIndex : options.length - 1);
        return;
      }

      setActiveIndex((currentIndex) => {
        const nextIndex = currentIndex < 0 ? options.length - 1 : Math.max(currentIndex - 1, 0);
        return nextIndex;
      });
      return;
    }

    if (event.key === "Enter" && isOpen) {
      event.preventDefault();
      selectOption(activeIndex >= 0 ? activeIndex : 0);
      return;
    }

    if (event.key === "Escape" || event.key === "Tab") {
      setIsOpen(false);
    }
  };

  const handleOptionMouseDown = (event: MouseEvent<HTMLLIElement>): void => {
    event.preventDefault();
  };

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
        value={selectedLabel}
        placeholder={placeholder}
        readOnly
        onClick={() => {
          if (isOpen) {
            setIsOpen(false);
            return;
          }

          openList(selectedIndex >= 0 ? selectedIndex : 0);
        }}
        onKeyDown={handleInputKeyDown}
      />

      {isOpen ? (
        <ul
          id={listboxId}
          role="listbox"
          className="[position:absolute] [top:calc(100%_+_var(--radius-sm))] [left:0] [right:0] [display:flex] [flex-direction:column] [gap:var(--radius-sm)] [margin:0] [padding:var(--radius-sm)] [list-style:none] [background:var(--bg-elevated)] [border:1px_solid_var(--border-default)] [border-radius:var(--radius-md)] [box-shadow:var(--shadow-md)] [z-index:10]"
        >
          {options.map((option, index) => {
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
                  selectOption(index);
                }}
              >
                {option.label}
              </li>
            );
          })}
        </ul>
      ) : null}
    </div>
  );
}

export { AccessibleCombobox };
