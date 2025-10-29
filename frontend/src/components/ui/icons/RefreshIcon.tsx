
const RefreshIcon = ({ size = 18, color = "currentColor" }) => (
  <svg xmlns="http://www.w3.org/2000/svg" 
       width={size} height={size} fill="none" 
       stroke={color} strokeWidth="2" 
       strokeLinecap="round" strokeLinejoin="round" 
       className="icon icon-refresh"
        viewBox="0 0 24 24">
    <polyline points="23 4 23 10 17 10" />
    <polyline points="1 20 1 14 7 14" />
    <path d="M3.51 9a9 9 0 0 1 14.13-3.36L23 10" />
    <path d="M20.49 15A9 9 0 0 1 9.87 20.36L1 14" />
  </svg>
);

export default RefreshIcon;
