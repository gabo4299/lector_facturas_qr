

const DeleteIcon = ({ size = 18, color = "currentColor" }) => (
  <svg xmlns="http://www.w3.org/2000/svg" 
       width={size} height={size} fill="none" 
       stroke={color} strokeWidth="1" 
       strokeLinecap="round" strokeLinejoin="round" 
       className="icon icon-trash"
        viewBox="0 0 24 24">

    <polyline points="3 6 5 6 21 6" />
    <path d="M19 6L17.5 20H6.5L5 6" />
    <path d="M10 11V17" />
    <path d="M14 11V17" />
    <path d="M9 6V4H15V6" />
  </svg>
);

export default DeleteIcon;
