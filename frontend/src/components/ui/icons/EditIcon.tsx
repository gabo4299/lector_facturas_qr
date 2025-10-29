
const EditIcon = ({ size = 18, color = "currentColor" }) => (
  <svg xmlns="http://www.w3.org/2000/svg" 
       width={size} height={size} fill="none" 
       stroke={color} strokeWidth="2" 
       strokeLinecap="round" strokeLinejoin="round" 
       className="icon icon-edit"
        viewBox="0 0 24 24">
    <path d="M12 20h9" />
    <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z" />
  </svg>
);

export default EditIcon;
