import customtkinter as ctk
from send_query_reusable import query_rag
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Local RAG ChatBot")
        self.geometry("900x720")

        # Display Chat
        self.chat_box = ctk.CTkTextbox(
            self,
            width  = 850,
            height = 550,
            wrap   = "word"
        )
        self.chat_box.pack(
            padx   = 20,
            pady   = 20,
            fill   = "both",
            expand = True
        )

        # Bottom frame
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(
            padx = 20,
            pady = 20,
            fill = "x"
        )

        # User input
        self.entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text = "Ask something..."
        )
        self.entry.pack(
            side   = "left",
            padx   = 10,
            pady   = 10,
            fill   = "x",
            expand = True
        )
        self.entry.bind(
            "<Return>",
            lambda evend: self.send_message()
        )

        # Send button
        self.send_button = ctk.CTkButton(
            self.input_frame,
            text    = "Send",
            command = self.send_message
        )
        self.send_button.pack(
            side = "right",
            padx = 10
        )

    def send_message(self):
        question = self.entry.get().strip()
        if not question:
            return
        
        self.entry.delete(
            0,
            "end"
        )

        self.chat_box.insert(
            "end",
            f"\nAssistant is thinking\n"
        )

        # Run Ollama in another thread
        threading.Thread(
            target = self.get_answer,
            args   = (question,),
            daemon = True
        ).start()


    def get_answer(self, question):
        result = query_rag(question)
        answer = result["answer"]
        sources = "\n".join(
            f"- {s['source']} page {s['page']}" for s in result["sources"]
        )

        self.after(
            0,
            self.update_chat,
            answer,
            sources
        )


    def update_chat(self, answer, sources):
        self.chat_box.delete(
            "end-3l",
            "end"
        )
        self.chat_box.insert(
            "end",
            f"\nAssistant:\n{answer}\n"
        )
        self.chat_box.insert(
            "end",
            f"\nSources:\n{sources}\n"
        )

if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()