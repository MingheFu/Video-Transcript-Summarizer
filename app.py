from flask import Flask, jsonify, request, abort
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import Formatter
from transformers import T5ForConditionalGeneration, T5Tokenizer
import re

app = Flask(__name__)

@app.route('/')
def welcome():
    return jsonify(message="Welcome to the YouTube Transcript Summarizer API")

def get_youtube_video_transcript(video_id):
    return YouTubeTranscriptApi.get_transcript(video_id)

class StringFormatter(Formatter):
    def format_transcript(self, transcript_list, **kwargs):
        string_transcript = ' '.join([transcript_list['text']])
        return string_transcript


    def format_transcripts(self, transcripts, **kwargs):
        string_transcript = ' '.join([transcript['text'] for transcript in transcripts])
        return string_transcript

def abstract_summarization(transcript):
    model = T5ForConditionalGeneration.from_pretrained("t5-base")
    tokenizer = T5Tokenizer.from_pretrained("t5-base")
    words = transcript.split()
    #if len(words) > 1024:
    #     raise ValueError("Exceeds maximum length")

    def split_into_chunks(words, max_chunk_size = 1024):
        for i in range(0, len(words), max_chunk_size):
            yield " ".join(words[i:i + max_chunk_size])

    summaries = []
    try:
        for chunk in split_into_chunks(words):
            inputs = tokenizer.encode("summarize: " + chunk, return_tensors = "pt",
                                      max_length = 512, truncation = True)
            outputs = model.generate(inputs,
                                     max_length = 150,
                                     min_length = 40,
                                     length_penalty = 2.0,
                                     num_beams = 4,
                                     early_stopping = True)
            summary = tokenizer.decode(outputs[0], skip_special_tokens = True)
            summaries.append(summary)
    except Exception as e:
        print(f"Error: {e}")
        summaries.append("[Error occurred while processing]")

    # combine the summary
    return " ".join(summaries)

def extract_video_id(url):
    # ues regex
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

@app.route('/api/summarize', methods=['GET'])
def get_summary():
    youtube_url = request.args.get('youtube_url', '')
    if not youtube_url:
        abort(400, description = "Invalid url")
    video_id = extract_video_id(youtube_url)
    if not video_id:
        abort(400, description = "Invalid YouTube URL")
    try:

        transcript_list = get_youtube_video_transcript(video_id)
        form = StringFormatter()
        transcript = form.format_transcripts(transcript_list)
        summary = abstract_summarization(transcript)

        return jsonify(summary = summary), 200
    except ValueError as ve:
        abort(400, description = str(ve))
    except Exception as e:
        abort(500, description = f"Error: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)
