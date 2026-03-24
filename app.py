import os
import whisper
import openai
import tempfile
import pyaudio
import wave
from gtts import gTTS
import playsound

# Configuração da chave da API (NÃO DEIXE SUA CHAVE AQUI!)
# Use uma variável de ambiente ou configure via terminal
openai.api_key = os.getenv("OPENAI_API_KEY")

def gravar_audio(duracao=5, taxa_amostragem=16000):
    """Grava áudio do microfone por 'duracao' segundos e salva em arquivo temporário"""
    formato = pyaudio.paInt16
    canais = 1
    taxa = taxa_amostragem
    chunk = 1024

    p = pyaudio.PyAudio()
    stream = p.open(format=formato, channels=canais, rate=taxa,
                    input=True, frames_per_buffer=chunk)

    frames = []
    print("🎤 Gravando...")
    for _ in range(0, int(taxa / chunk * duracao)):
        data = stream.read(chunk)
        frames.append(data)

    print("✅ Gravação concluída.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        wf = wave.open(tmpfile.name, 'wb')
        wf.setnchannels(canais)
        wf.setsampwidth(p.get_sample_size(formato))
        wf.setframerate(taxa)
        wf.writeframes(b''.join(frames))
        wf.close()
        return tmpfile.name

def transcrever_audio(caminho_audio):
    """Usa o Whisper para transcrever áudio para texto"""
    model = whisper.load_model("base")
    result = model.transcribe(caminho_audio)
    return result["text"]

def perguntar_chatgpt(pergunta):
    """Envia pergunta para o ChatGPT e retorna resposta"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": pergunta}
            ],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro ao obter resposta: {e}"

def sintetizar_voz(texto):
    """Converte texto em áudio usando gTTS e reproduz"""
    tts = gTTS(text=texto, lang='pt')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        tts.save(tmpfile.name)
        playsound.playsound(tmpfile.name)

def main():
    if not openai.api_key:
        print("❌ ERRO: Defina a variável de ambiente OPENAI_API_KEY com sua chave.")
        return

    # 1. Gravar pergunta
    arquivo_audio = gravar_audio(duracao=5)  # ajuste a duração conforme necessário

    # 2. Transcrever
    pergunta = transcrever_audio(arquivo_audio)
    print(f"📝 Você perguntou: {pergunta}")

    # 3. Perguntar ao ChatGPT
    resposta = perguntar_chatgpt(pergunta)
    print(f"🤖 Resposta: {resposta}")

    # 4. Sintetizar voz
    sintetizar_voz(resposta)

if __name__ == "__main__":
    main()
