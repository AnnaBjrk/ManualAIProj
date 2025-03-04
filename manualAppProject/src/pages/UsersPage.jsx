import React, { useState, useEffect } from "react";
import cuteRob from "../assets/img/diskmPersp.jpg";
import UploadManual from "../components/UploadManual";

export default function UsersPage() {
    const [firstName, setFirstName] = useState('');

    useEffect(() => {
        const rawData = localStorage.getItem('user');
        console.log('Raw data:', rawData);

        const userData = JSON.parse(rawData);
        console.log('Parsed data:', userData);

        if (userData && userData.firstName) {
            setFirstName(userData.firstName);
            console.log('Setting firstName to:', userData.firstName);
        }
    }, []);

    return (
        <div className="flex flex-col p-4 max-w-4xl mx-10">
            <h1 className="font-['Roboto'] text-5xl mb-6">{firstName}s manualer</h1>

            <div className="flex justify-left mb-8">
                <img
                    className="h-64 w-auto object-contain"
                    src={cuteRob}
                    alt="söt robot"
                />
            </div>

            <p className="text-gray-700 font-['Roboto'] leading-relaxed">
                Olika gör oss vidsträckt rot som på det blivit, ingalunda miljoner trevnadens se ingalunda träutensilierna bäckasiner kanske lax, söka från bra sax ordningens faktor verkligen. Kanske groda om regn rännil vidsträckt färdväg dag ta denna flera själv, kan så där inom samtidigt erfarenheter räv där precis bland, dag miljoner från bland och kunde ingalunda bland groda äng. Hela stora dock om kanske och stig varit sista, träutensilierna annat hans verkligen år åker dimma, smultron flera hwila träutensilierna kanske både som.
            </p>
        </div>
    );

    <div>
        <UploadManual>

        </UploadManual>


    </div>


}