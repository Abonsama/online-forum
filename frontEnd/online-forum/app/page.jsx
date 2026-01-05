import React from 'react';
import NavBar from '../components/navBar';
import ThreadsMenu from '../components/threadsMenu';
import Link from 'next/link';
import TrendingTopics from '../components/trendingTopics.jsx';
import Messages from '../components/messages';
export default function Home() {
    return(
        <main>
            <header>
                <Link href="/">Online Forum</Link>
            </header>
            <aside>
                {/* navbar */}
                <NavBar />
                {/* threadmenus */}
                <ThreadsMenu />
                {/* production */}
            </aside>
            <section>
                {/* mainsection */}
            </section>
            <aside>
                {/* loginButton */}
                <Link href="/loginPage">Login</Link>
                {/* userProfile */}
                <Link href="/profile">Profile</Link>
                {/* trendingTopics */}
                <TrendingTopics />
                {/* messages */}
                <Messages />
            </aside>
        </main>
    );
}
