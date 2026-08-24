import { useState } from 'react'
import { ImageIcon } from 'lucide-react'

export default function ProductThumb({ src, alt, className = '' }) {
  const [failed, setFailed] = useState(false)

  if (!src || failed) {
    return (
      <div
        className={`flex items-center justify-center bg-[#EEF2F6] text-[#718096] ${className}`}
        aria-hidden="true"
      >
        <ImageIcon className="h-1/2 w-1/2" />
      </div>
    )
  }

  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      onError={() => setFailed(true)}
      className={`object-cover ${className}`}
    />
  )
}