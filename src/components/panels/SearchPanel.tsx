export function SearchPanel() {
  return (
    <div className="flex flex-col gap-3">
      <input
        type="text"
        placeholder="Search apps, files, web..."
        autoFocus
        className="
          w-full px-4 py-2.5 rounded-xl
          bg-white/10 border border-white/10
          text-white text-sm placeholder-white/30
          outline-none focus:border-white/25
          transition-colors
        "
      />
      <div className="text-white/30 text-xs text-center py-4">
        Start typing to search
      </div>
    </div>
  )
}
