import React from "react";
import cuteRob from "../assets/img/diskmPersp.jpg";
import logo1 from "../assets/digizen.png";
import logo2 from "../assets/domezen.png";
import logo3 from "../assets/electromax.png";
import logo4 from "../assets/technova.png";
import logo5 from "../assets/jechcove.png";
import logo6 from "../assets/domizen.png";

export default function About() {
    return (
        <div className="flex flex-col p-4 max-w-4xl mx-10">
            <h1 className="font-['Neucha'] text-5xl mb-6">Om oss</h1>



            <p className="text-gray-700 font-['Barlow_Condensed'] leading-relaxed mb-8">
                Gizmo Buddy är en gratis tjänst som hjälper dig att spara och hitta manualer till din hemelektronik och dina hushållsapparater. Slipp borttappade instruktionsböcker – med vår tjänst har du alltid rätt manual nära till hands!
                <br /><br />
                Tjänsten är just nu en prototyp - och är utvecklad av Anna Björklund, student i pythonutveckling inom AI på Nackademin.
                I vår databas finns manualer från fiktiva företag som TechNova, ElektroMax, HomeEase och DigiCore. Registrera dig idag och få enkel tillgång till alla dina manualer på ett ställe!
            </p>

            <h2 className="font-['Neucha'] text-3xl mb-6">Våra partners</h2>

            {/* First row of logos */}
            <div className="flex flex-row justify-between mb-8">
                <img
                    className="h-32 w-auto object-contain"
                    src={logo1}
                    alt="DigiZen logo"
                />
                <img
                    className="h-32 w-auto object-contain"
                    src={logo2}
                    alt="DomeZen logo"
                />
                <img
                    className="h-32 w-auto object-contain"
                    src={logo3}
                    alt="ElectroMax logo"
                />
            </div>

            {/* Second row of logos */}
            <div className="flex flex-row justify-between mb-8">
                <img
                    className="h-32 w-auto object-contain"
                    src={logo4}
                    alt="TechNova logo"
                />
                <img
                    className="h-32 w-auto object-contain"
                    src={logo5}
                    alt="JechCove logo"
                />
                <img
                    className="h-32 w-auto object-contain"
                    src={logo6}
                    alt="DomiZen logo"
                />
            </div>
        </div>
    );
}