import React, { useState } from "react";
import Sidebar from '../components/Sidebar'
import { Outlet } from 'react-router-dom';
export default function MainLayout() {

    return (
        <div className="min-h-screen flex flex-col md:flex-row bg-linear-to-r from-[#7b1d1d] via-[#9c421b] to-[#912813]">
            <Sidebar/>
            <main className="relative flex-1 min-w-0 min-h-screen">
                <Outlet/>
            </main>

        </div>

    )
}
