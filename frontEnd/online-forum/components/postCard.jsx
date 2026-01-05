// its for the layout of each post card in the main section
// post data will be passed as props later 
// make it able to display multiple content types and show more than one image if needed
// it will the post data such as content, likes, comments, shares, etc.
// it will have the content of the post itself text image video link etc.
import Image from 'next/image';
export default function PostCard({data, content}) {
    function handleUpvote() {}
    function handleDownvote() {}
    function handleComment() {}
    function handleShare() {}
    function handleMultipleMedia(array) {
        // output multiple images or videos if there are more than one
        // you just pass the property of object that contains the array of media example data.images or data.videos
    }
    return (
        <div className="post-card">
            <div className="post-content">
                {content.post? <p>{content.post}</p>:""}
                {/* {content.Image?<Image src={content.image} alt={data.imageAlt}/>:""}
                {content.video?<video src={content.video} alt={data.videoAlt}/>:""} */}
                {handleMultipleMedia(content.image)}
                {handleMultipleMedia(content.video)}
            </div>
            <div className='postButtons'>
            <button onClick={handleUpvote}>upvote {data.upvote}</button>
            <button onClick={handleDownvote}>downvote {data.downvote}</button>
            <button onClick={handleComment}>Comment {data.comments}</button>
            <button onClick={handleShare}>Share {data.shares}</button>
            </div>
        </div>
                );
}