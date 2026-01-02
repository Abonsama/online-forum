// here are the list of all threads that users create or make favorite
import Link from 'next/link';
import React from 'react';

export default function threadmenus() {
    return(
        <>
            <span>threads</span>
            <nav>
                <ul>
                    <li>
                        <Link href="/">newthread</Link>
                    </li>
                    <li>
                        <Link href="/">general</Link>
                    </li>
                    {/* <li>
                        <Link href="/"></Link>
                        </li> */}
                    <li>
                        <input type="text" placeholder="Search threads..." />
                    </li>
                </ul>
            </nav>
        </>
    );
}