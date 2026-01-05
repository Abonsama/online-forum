import PostCard from "./postCard";
// fetch post data from backend later it must have the data of what is in the post in boolean form and content of the post itself

export default function MainSection() {
    return (
        <div>
            <PostCard data={data} content={content} />
        </div>
    );
}
// main section where users can see posts and threads