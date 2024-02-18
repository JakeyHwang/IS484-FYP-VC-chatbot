"use client";
import React, { useState } from 'react';
const ChatBar = ({ sendMsg }) => {
    const [message, setMessage] = useState('');

    const handleChange = (e) => {
        console.log(e);
        setMessage(e.target.value);
    }

    const handleSend = () => {
        if (message.trim()) {
            sendMsg(message);
            setMessage('');  
        }
    }

    return (
        <div className="fixed bottom-0 left-8 m-12 w-full flex">
            {/* <input id="chat" type="text" placeholder="Ask me anything..." className='bg-[#e5e5e5] rounded-lg px-4 py-1 w-3/5' value={message} onChange={handleChange} />
            <button className="mx-2 right-5 bg-[#7dd3fc] rounded-lg px-4 py-1" onClick={handleSend}>Send</button> */}
            <input id="chat" type="text" placeholder="Ask me anything..." className='border border-black bg-[#fffff] rounded-full px-4 py-1 w-3/5' value={message} onChange={handleChange} onKeyDown={(e)=>{if(e.key==='Enter'){handleSend()}}} />
            <button className={`mx-2 right-5 text-white rounded-full px-4 py-4 ${!message.trim() ? 'bg-[#4f65e5] focus:outline-none' : 'bg-[#7dd3fc]'}`} onClick={handleSend} disabled={!message.trim()}>
            </button>
        </div>
    );
}

const Sidebar = ({ chatTitles, changeTopic, currentIndex, handleNewChat }) => {
    const handleNewTopic = (i) => {
        changeTopic(i);
    }

    return (
        <div id="histlog" className="bg-[#d7e3fb] w-1/5 h-screen flex flex-col">
            {/*Verchat Logo*/}
            <div className="flex justify-center">
                <img src="./verchat_logo.png" alt="Sidebar Image" />
            </div>
            {/* New Chat button */}
            <div className="flex justify-center">
                <button className="bg-[#7dd3fc] rounded-lg px-4 py-1 mx-2" onClick={handleNewChat}>
                    New Chat
                </button>
            </div>
            <h1 className='text-center'>Chat History</h1>
            {/* Display chat history in reverse order */}
            {chatTitles.slice(0).reverse().map((title, index) => (
                <div key={index} className='flex flex-col items-center justify-center'>
                    <button id={index} className={index != currentIndex ? `bg-blue-500 hover:bg-blue-700 text-white font-bold px-2 m-2 border border-blue-700 rounded` : 'text-white bg-[#4B5563] dark:bg-[#4B5563] cursor-not-allowed font-bold px-2 m-2 text-center border border-[#111827] rounded'} disabled={index == currentIndex} onClick={handleNewTopic}>{title}</button>
                </div>
            ))}
        </div>
    );
}

const WlcMsg = () => {
    return (
            <div className="">
                <h1 className='bg-[#d7e3fb] rounded-lg px-2 py-1 col-start-1 col-end-2'>Hi, how may I help you today?</h1>
            </div>     
    );
}

const NewChat = () => {
    const chatTitle = "Untitled Chat2";
    const [currentIndex, setCurrentIndex] = useState(0);
    const [currentChatTitle, setCurrentChatTitle] = useState(chatTitle);
    const [chatHistory, setChatHistory] = useState([]);
    const [chatTitles, setChatTitles] = useState([currentChatTitle]);
    const [chatHistories, setChatHistories] = useState({});

    const handleNewChat = () => {
        console.log('Creating a new chat...');
        console.log(chatHistory);
        setChatTitles([...chatTitles, currentChatTitle]); // Add the current chat title to the list of chat titles
        setChatHistories({ ...chatHistories, [chatTitles.length - currentIndex - 1]: chatHistory }); // Add the current chat history to the list of chat histories
        setChatHistory([]); // Clear chat history when starting a new chat
        setCurrentChatTitle(chatTitle); // Reset chat title to the placeholder
    };

    const handleSend = (msg) => {
        const updatedChatHistory = [...chatHistory, { type: 'user', message: msg }];
        setChatHistory(updatedChatHistory);
    };

    const handleChangeTopic = (i) => {
        setChatHistories({ ...chatHistories, [chatTitles.length - currentIndex - 1]: chatHistory })
        setCurrentIndex(i.target.id);
        setCurrentChatTitle(chatTitles[chatTitles.length + ((Number(i.target.id) + 1) * -1)]);
        setChatHistory(chatHistories[chatTitles.length + ((Number(i.target.id) + 1) * -1)]);
    }

    return (
        <div className="flex">
            <Sidebar chatTitles={chatTitles} changeTopic={(i) => { handleChangeTopic(i) }} currentIndex={currentIndex} handleNewChat={handleNewChat} />
            <div className="flex-auto">
                <div className='grid grid-flow-row auto-rows-max grid-cols-2 gap-y-4 mx-2'>
                    <WlcMsg />
                   {/* Display chat history */}
                <div className="flex flex-col-reverse">
                {chatHistory.slice(0).reverse().map((chat, index) => (
                <div key={index} className={chat.type === 'user' ? 'user-message' : 'bot-message'}>
                <div className={`bg-[#e4e4e4] rounded-lg px-2 py-1 text-wrap mb-2 ${chat.type === 'user' ? 'ml-auto' : 'mr-auto'}`} >
                <h1>{chat.message}</h1>
            </div>
            </div>
            ))}
        </div>


                    {/* Assuming sendMsg is defined */}
                    <ChatBar sendMsg={(msg) => { handleSend(msg); }} />
                </div>
            </div>
        </div>
    );
}

export default NewChat;

// const handleSend = () => {
//         if (message.trim()) {
//             sendMsg(message);
//             setMessage('');  
//         }
//     }

//     return (
//         <div className="fixed bottom-0 left-0 m-12 w-full">
//             <button className="left-0 bg-[#7dd3fc] rounded-lg px-4 py-1 mx-2" onClick={handleNewChat}>
//                 New Chat
//             </button>
//             <input id="chat" type="text" placeholder="Ask me anything..." className='bg-[#e5e5e5] rounded-lg px-4 py-1 w-3/5' value={message} onChange={handleChange} onKeyDown={(e)=>{if(e.key==='Enter'){handleSend()}}} />
//             <button className={`mx-2 right-5 text-white rounded-lg px-4 py-1 ${!message.trim() ? 'bg-red-300 focus:outline-none' : 'bg-[#7dd3fc]'}`} onClick={handleSend} disabled={!message.trim()}>
//                 Send
//             </button>
//         </div>
//     );