// this is the main navigation bar component for the online forum application containing the searchbar 
import Link from 'next/link';
import React from 'react';

export default function NavBar() {
    return(
        <>
            <nav>
                <ul>
                    <li>
                        <Link href="/">home</Link>
                    </li>
                    <li>
                        <Link href="/">news</Link>
                    </li>
                    <li>
                        <input type="text" placeholder="Search..." />
                    </li>
                </ul>
            </nav>
        </>
    );
}