import { useState } from "react";

export default function UserBlock({ name, score = 0 }) {
  return (
    <div className="w-full max-w-2xl bg-white/30 backdrop-blur-md border border-white/20 shadow-xl p-4 rounded-2xl flex items-center justify-between transition-all hover:scale-[1.01]">
      <div className="flex items-center gap-4">
        <span className="text-gray-900 font-medium truncate max-w-[200px] sm:max-w-xs">
          {name}
        </span>
      </div>
    </div>
  );
}