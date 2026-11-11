import React from 'react';
import { AlertTriangle, ArrowLeft, RefreshCw } from 'lucide-react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Unhandled Application Render Error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[60vh] max-w-xl mx-auto px-4 py-16 flex flex-col items-center justify-center text-center font-mono space-y-4">
          <div className="w-12 h-12 rounded-xl bg-rose-500/10 dark:bg-rose-950/40 border border-rose-500/30 dark:border-rose-900/60 flex items-center justify-center text-rose-600 dark:text-rose-400">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div className="space-y-1.5">
            <h2 className="text-base font-semibold text-[#1c1917] dark:text-zinc-100">
              Something went wrong while displaying this view
            </h2>
            <p className="text-xs text-[#5c5549] dark:text-zinc-400 max-w-md leading-relaxed">
              {this.state.error?.message || 'An unexpected rendering error occurred.'}
            </p>
          </div>
          <div className="flex items-center gap-2 pt-2">
            <button
              type="button"
              onClick={this.handleReset}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-[#1c1917] hover:bg-[#292524] text-[#faf5ec] dark:bg-zinc-100 dark:hover:bg-white dark:text-zinc-950 text-xs font-medium cursor-pointer transition-all active:scale-95 shadow-xs"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Return to Dashboard</span>
            </button>
            <button
              type="button"
              onClick={() => window.location.reload()}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-[#faf5ec] hover:bg-[#e2d9c7] text-[#1c1917] border border-[#d5cbba] dark:bg-zinc-900 dark:hover:bg-zinc-800 dark:text-zinc-300 dark:border-zinc-800 text-xs transition-colors cursor-pointer active:scale-95 shadow-2xs"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Reload Page</span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
