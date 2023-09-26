# AskPDF-multi
A simple web application that allows users to upload PDFs and ask questions about their content. The application uses a language model run locally (currently set up to llama-2 7b gguf, but can use any supported by langchain) to provide answers based on the uploaded PDFs.

## Features

- Upload multiple PDFs at once.
- Ask questions about the content of the uploaded PDFs.
- Get answers in a chat-like interface.
- Markdown rendering for bot responses.

## Setup & Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/btcodeorange/askpdf-multi.git
   cd askpdf-multi
2. **Install Dependencies**

   Make sure you have the required libraries and dependencies installed.
   Also make sure you have downloaded a GGUF file to run. The script is setup to run the file: https://huggingface.co/TheBloke/Llama-2-7b-Chat-GGUF/blob/main/llama-2-7b-chat.Q4_K_M.gguf at the moment, but any langchain supported model should be fine. 

4. **Run the Backend Server**

   ```bash
   python ai2fast.py
   ```

   This will start the FastAPI server on `http://0.0.0.0:8000`.

5. **Open the Web Application**

   Navigate to `index.html` in your browser to start using the application.

## Usage

1. Click on the file input to select and upload your PDFs.
2. Once uploaded, type your question in the input box below.
3. Click "Send" to get an answer based on the content of the uploaded PDFs.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
