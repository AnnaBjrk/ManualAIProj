import React from "react";


export default function Footer() {
    return (


        <footer className=" font-['Roboto'] justify-end mb-auto bg-sky-800 mt-6 px-2 py-4 ">
            <a href="about.html" className="ml-4 text-amber-50 hover:text-amber-500 text-lg hover:underline">Om
                Manual Assistant</a>
            <address className="ml-4 font-roboto text-lg not-italic text-amber-50">
                Torggatan 23,
                123 34 Stockholm
            </address>
            <p className="ml-4 font-roboto text-lg text-amber-50">
                Telefon <a href="tel:+46-734-567-800">+46 (0)734-567-800</a>
            </p>
        </footer>

    );
}