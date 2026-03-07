"use client";

import { Component, type ErrorInfo, type ReactNode } from "react";

interface ErrorBoundaryProps {
  children: ReactNode;
  fallbackMessage?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  public state: ErrorBoundaryState = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
    };
  }

  public componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("ErrorBoundary caught an error:", error);
    console.error("Component stack:", info.componentStack);
  }

  private handleRetry = (): void => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  public render(): ReactNode {
    if (!this.state.hasError) {
      return this.props.children;
    }

    const message = this.props.fallbackMessage ?? "Something went wrong.";

    return (
      <div
        role="alert"
        aria-live="assertive"
        className="[display:flex] [flex-direction:column] [align-items:flex-start] [gap:12px] [padding:16px] [background:var(--bg-elevated)] [border:1px_solid_var(--border-default)] [border-radius:var(--radius-lg)]"
      >
        <p className="badge badge-danger">{message}</p>
        <button
          type="button"
          onClick={this.handleRetry}
          className="btn-ghost"
        >
          Retry
        </button>
      </div>
    );
  }
}

export { ErrorBoundary };
