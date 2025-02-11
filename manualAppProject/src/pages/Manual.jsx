import React from "react";
import cuteRoundRob from "../assets/img/cuteRoundRob2.gif";

export default function Manual() {

    return (
        <div className="flex flex-col p-4 max-w-4xl mx-10">
            <h1 className="font-['Roboto'] text-5xl mb-6">Hitta en manual</h1>

            <div className="flex justify-left mb-8">
                <img
                    className="h-64 w-auto object-contain"
                    src={cuteRoundRob}
                    alt="söt robot"
                />
            </div>

            <p className="text-gray-700 font-['Roboto'] leading-relaxed">
                Olika gör oss vidsträckt rot som på det blivit, ingalunda miljoner trevnadens se ingalunda träutensilierna bäckasiner kanske lax, söka från bra sax ordningens faktor verkligen. Kanske groda om regn rännil vidsträckt färdväg dag ta denna flera själv, kan så där inom samtidigt erfarenheter räv där precis bland, dag miljoner från bland och kunde ingalunda bland groda äng. Hela stora dock om kanske och stig varit sista, träutensilierna annat hans verkligen år åker dimma, smultron flera hwila träutensilierna kanske både som.
            </p>
        </div>
    );
}