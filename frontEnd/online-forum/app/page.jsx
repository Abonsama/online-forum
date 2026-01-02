import React from 'react';
import NavBar from '../components/navBar';
import ThreadsMenu from '../components/threadsMenu';
export default function Home() {
    return(
        <main>
            <aside>
                {/* navbar */}
                <NavBar />
                {/* searchbar */}
                {/* threadmenus */}
                <ThreadsMenu />
                {/* production */}
            </aside>
            <section>
                {/* mainsection */}
            </section>
            <aside>
                {/* loginButton */}
                {/* userProfile */}
                {/* trendingTopics */}
                {/* messages */}
            </aside>
        </main>
    );
}
