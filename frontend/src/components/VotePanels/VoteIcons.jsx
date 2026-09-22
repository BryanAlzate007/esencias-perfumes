function Icon({ children, ...props }) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" {...props}>
      {children}
    </svg>
  );
}

export function HeartIcon(props) {
  return (
    <Icon fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
      <path d="M12 20s-7-4.4-7-9.2C5 8 6.8 6.4 9 6.4c1.3 0 2.4.6 3 1.6.6-1 1.7-1.6 3-1.6 2.2 0 4 1.6 4 4.4 0 4.8-7 9.2-7 9.2z" />
    </Icon>
  );
}

export function ClockIcon(props) {
  return (
    <Icon fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
      <circle cx="12" cy="12" r="8.2" />
      <path strokeLinecap="round" d="M12 8.2V12l2.6 2.2" />
    </Icon>
  );
}
