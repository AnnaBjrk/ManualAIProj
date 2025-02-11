import React from "react";
import { Link } from 'react-router-dom';
import tvattmTrumma from "../assets/img/orangeTvatt.jpg";
import plockaDiskm from "../assets/img/front_dishw.gif";
import letaKylskap from "../assets/img/PappaKylsk.jpeg";


export default function Index() {
    return (
        <div className="font-['Roboto']">
            <section className="m-5 p-8 bg-cover bg-center text-amber-50 text-right text-wrap rounded-lg"
                style={{ backgroundImage: "url('./src/assets/img/liten_tecknad_robot_bla.gif')" }}>
                <h1 className="text-5xl font-roboto mb-4">Manual Assistant <br /> din hjälp när <br />hemmatekniken strular
                </h1>
                <p className="text-lg font-roboto"> Hitta enkelt din manual och ta AI till hjälp för att lösa ditt problem.</p>
                {/* <a href="query.html"
                    className="inline-block mt-5 px-6 py-3 bg-amber-600 text-white rounded hover:bg-blue-700 transition-colors">
                    Fråga AI
                </a> */}
                <Link to="/query" className="text-white text-xl hover:text-white">
                    Query
                </Link>
            </section>




            <section className="grid grid-cols-3 gap-4 my-3">
                <div className="flex flex-col border-1 rounded-sm border-amber-900 m-2 shadow-lg shadow-blue-500/50">

                    {/* <img src="img/istockphoto-1958606045-1024x1024.jpg" className="pt-4 pl-4 pr-4" alt="dishwasher" /> */}
                    <div className="pt-4 pl-4 pr-4" alt="dishwasher">
                        <img className="letaKylskap" src={plockaDiskm} />
                    </div>
                    <h3 className="ml-4 text-amber-950">Lös ett problem</h3>
                    <button
                        className=" px-1 py-1 ml-4 mb-2 w-20 bg-sky-600 text-sm border rounded-sm border-sky-600 text-white">Fråga
                        AI</button>
                </div>



                <div className="flex flex-col border-1 rounded-sm border-amber-900 m-2 shadow-lg shadow-blue-500/50">

                    {/* <img src="img/istockphoto-1479370110-1024x1024.jpg" className="pt-4 pl-4 pr-4" alt="dishwasher" /> */}
                    <div className="pt-4 pl-4 pr-4" alt="dishwasher">
                        <img className="letaKylskap" src={tvattmTrumma} />
                    </div>
                    <h3 className="ml-4 text-amber-950">Hitta en manual</h3>
                    <button
                        className=" px-1 py-1 ml-4 mb-2 w-30 bg-sky-600 text-sm border rounded-sm border-sky-600 text-white">Sök
                        manual</button>
                </div>

                <div className="flex flex-col border-1 rounded-sm border-amber-900 m-2 shadow-lg shadow-blue-500/50">

                    {/* <img src="img/washing-machine-7741655_1280.jpg" className="pt-4 pl-4 pr-4" alt="dishwasher" /> */}
                    <div className="pt-4 pl-4 pr-4" alt="dishwasher">
                        <img className="letaKylskap" src={letaKylskap} />
                    </div>
                    <h3 className="ml-4 text-amber-950">Våra samarbetspartners</h3>
                    <button
                        className=" px-1 py-1 ml-4 mb-2 w-30 bg-sky-600 text-sm border rounded-sm border-sky-600 text-white">Se
                        hela listan</button>
                </div>

            </section>


        </div>
    );


}