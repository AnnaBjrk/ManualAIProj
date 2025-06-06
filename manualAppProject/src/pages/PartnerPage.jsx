import React from "react";
import cuteRob from "../assets/img/diskmPersp.jpg";
import AdminManualsTable from "../components/AdminManualsTable";
import StatisticPartnerManuals from "../components/StatisticPartnerManuals";
import UploadManual from "../components/UploadManual";


export default function PartnerPage() {


    return (
        <div className="flex flex-col p-4 max-w-4xl mx-10">
            <h1 className="font-['Neucha'] text-5xl mb-6">Sida för partners</h1>

            <div>
                <StatisticPartnerManuals />
            </div>
            <div>
                <AdminManualsTable />
            </div>
            <div>
                <UploadManual />
            </div>

            <p className="text-gray-700 font-['Barlow_Condensed'] leading-relaxed">
                Olika gör oss vidsträckt rot som på det blivit, ingalunda miljoner trevnadens se ingalunda träutensilierna bäckasiner kanske lax, söka från bra sax ordningens faktor verkligen. Kanske groda om regn rännil vidsträckt färdväg dag ta denna flera själv, kan så där inom samtidigt erfarenheter räv där precis bland, dag miljoner från bland och kunde ingalunda bland groda äng. Hela stora dock om kanske och stig varit sista, träutensilierna annat hans verkligen år åker dimma, smultron flera hwila träutensilierna kanske både som.
            </p>
        </div>
    );
}

