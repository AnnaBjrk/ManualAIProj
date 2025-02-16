import React from "react";


export default function Footer() {
    return (


        <footer className=" font-['Neucha'] justify-end mb-auto border-t border-t-4 border-t-amber-50 border-double bg-sky-900 mt-6 px-2 py-4 ">
            <div className="mb-7 ">
                <a href="about.html" className="ml-4 text-amber-50 hover:text-amber-500 text-base hover:underline">Om
                    Gizmo buddy</a>
                <address className="ml-4 font-['Barlow_Condensed'] text-base not-italic text-amber-50">
                    Torggatan 23,
                    123 34 Stockholm
                </address>
                <p className="ml-4 font-['Barlow_Condensed'] text-base text-amber-50">
                    Telefon <a href="tel:+46-734-567-800">+46 (0)734-567-800</a>
                </p>
            </div>
        </footer>

    );
}