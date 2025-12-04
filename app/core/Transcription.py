from transformers import AudioFlamingo3ForConditionalGeneration, AutoProcessor

model_id = "nvidia/audio-flamingo-3-hf"
processor = AutoProcessor.from_pretrained(model_id)
model = AudioFlamingo3ForConditionalGeneration.from_pretrained(
    model_id, device_map="cpu"
)

def transcribe(audio_file):
    conversation = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Transcribe the input speech audio just output transcribe text from the output"},
                {"type": "audio", "path": audio_file},
            ],
        }
    ]

    inputs = processor.apply_chat_template(
        conversation,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
    ).to(model.device)

    outputs = model.generate(**inputs, max_new_tokens=500)
    text = processor.batch_decode(outputs[:, inputs.input_ids.shape[1]:],
                                  skip_special_tokens=True)
    return text[0]

if __name__=="__main__":
    text = transcribe("audio.wav")
    print(text)