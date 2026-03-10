import React, { useState } from "react";
import Sidebar from '../components/sidebar'
import { Outlet } from 'react-router-dom';
export default function MainLayout() {

    return (
        <div className="flex flex-row bg-linear-to-r from-[#7b1d1d] via-[#9c421b] to-[#912813]">
            <Sidebar/>
            <Outlet/>

        </div>

    )
}