import React from "react";
import gizmo from "../assets/gizmofixer_long3.jpg";
import AskGizmo from "../components/AskGizmo";


export default function Query() {


    return (
        <div className="flex flex-col p-4 max-w-4xl mx-10">
            <h1 className="font-['Neucha'] text-5xl mb-6">Gizmo - problemlösaren</h1>

            <div className="flex justify-left mb-8">
                <img
                    className="h-64 w-auto object-contain"
                    src={gizmo}
                    alt="söt robot"
                />
            </div>

            <div>
                <AskGizmo />
            </div>

            <p className="text-gray-700 font-['Barlow_Condensed'] leading-relaxed">
                Gizmo är en AI agent som tar hjälp av en large language model för att svara på din fråga. Som alla AI agenter så tar den fel då och då. Dubbelkolla i manualen om något verkar konstigt eller inte fungerar.
            </p>
        </div>
    );
}