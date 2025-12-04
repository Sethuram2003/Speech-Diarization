from app.core.Models import model_store

def transcribe(audio_file):
    processor = model_store.flamingo_processor
    model = model_store.flamingo_model
    
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