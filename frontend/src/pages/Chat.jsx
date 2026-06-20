import { useState } from "react";
import {chat} from "../services/api";
import { useLocation } from "react-router-dom";

function Chat(){
    const [question,setquestion]=useState("")
    const [messages,setMessages]=useState([]);
    const location = useLocation();
    const repoId = location.state?.repoId;

    const sendMessage=async () => {
        if(!question)return ;
        const usermessage={
            role:"user",
            text:question
     }
     setMessages((prev)=>[...prev,usermessage] );
     const res = await chat(repoId, question);

    const botMsg = {
      role: "bot",
      text: res.data.answer
    };

    setMessages((prev) => [...prev, botMsg]);

    setquestion("");
  };
return(<div className="p-10">

      <div className="h-[80vh] overflow-auto">

        {messages.map((msg, index) => (
          <div key={index}>
            <b>{msg.role}:</b> {msg.text}
          </div>
        ))}

      </div>

      <input
        className="border p-3 w-[80%]"
        value={question}
        onChange={(e) => setquestion(e.target.value)}
      />

      <button
        onClick={sendMessage}
        className="ml-4 bg-black text-white px-5 py-3"
      >
        Send
      </button>

    </div>);
}
export default Chat