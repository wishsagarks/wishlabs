import React from "react";
import { MacbookScroll } from "../ui/macbook-scroll";

 
export  default function MacbookScrollDemo() {
  return (
    <div className="overflow-hidden dark:bg-[#0B0B0F] bg-white w-full">
      <MacbookScroll
        title={
          <span>
           Innovating AI, one idea at a time.
          </span>
        }
      />
    </div>
  );
}