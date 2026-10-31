const paths = {
  shieldCode: "M12 2 3 5v7c0 5 9 10 9 10s9-5 9-10V5l-9-3Z M9 9l-3 3 3 3m6-6 3 3-3 3m-2-7-2 8",
  chevron: "m9 5 7 7-7 7",
  link: "m10 13 4-4m-5 7-2 2a4 4 0 0 1-6-6l4-4a4 4 0 0 1 6 0m2 0 2-2a4 4 0 0 1 6 6l-4 4a4 4 0 0 1-6 0",
  book: "M12 5v15M3 4h5c2 0 4 1 4 2 0-1 2-2 4-2h5v15h-5c-2 0-4 1-4 2 0-1-2-2-4-2H3V4Z",
  shield: "M12 3 4 6v6c0 5 8 9 8 9s8-4 8-9V6l-8-3Z M8.5 12l2.5 2.5 4.5-5",
  code: "m8 7-5 5 5 5m8-10 5 5-5 5m-3-13-2 16",
  upload: "M12 16V3m-5 5 5-5 5 5M4 15v5h16v-5",
  folder: "M3 7V5h6l2 3h10v12H3V7Z",
  github:
    "M9 19c-4 1-4-2-6-2m12 5v-4c0-1 .1-2-.5-2.5 4-.4 6.5-2 6.5-6A5 5 0 0 0 19.5 6c.2-1 .2-2-.3-3-2 0-3 1-4 1.5a15 15 0 0 0-6.4 0C7.8 4 6.8 3 4.8 3c-.5 1-.5 2-.3 3A5 5 0 0 0 3 9.5c0 4 2.5 5.6 6.5 6-.6.5-.5 1.5-.5 2.5v4",
  arrow: "M4 12h16m-6-6 6 6-6 6",
  check: "m5 12 4 4L19 6",
  alert: "m12 3 10 18H2L12 3Zm0 6v5m0 3h.01",
  file: "M14 2H5v20h14V7l-5-5Zm0 0v6h5M8 12h8m-8 4h5",
  info: "M12 11v6m0-10h.01 M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0",
  download: "M12 3v13m-5-5 5 5 5-5M4 16v5h16v-5",
} as const;
export function Icon({
  name,
  size = 20,
}: {
  name: keyof typeof paths;
  size?: number;
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d={paths[name]} />
    </svg>
  );
}
