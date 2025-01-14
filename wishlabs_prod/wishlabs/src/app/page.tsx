// page.tsx
import NavbarDemo from '../components/Landing/navbar'; 
import MacbookScrollDemo from '../components/Landing/macbook'
export default function Page() {
  return (
    <div className="overflow-hidden dark:bg-[#0B0B0F] bg-white w-full">
      <NavbarDemo />
      <MacbookScrollDemo/>
   
      <div className="p-4">
        <h1 className="text-2xl font-bold">Welcome to the Page!</h1>
        <p>This is where your main content will go.</p>
      </div>
    </div>
  );
}