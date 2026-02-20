#!/usr/bin/env python3
"""
English Audio Generation for Phonetic Research
音声学研究用の英語音声データセット生成ツール

This script generates English audio datasets for vowel research (F0, F1/F2 analysis)
and subsequent GLMM analysis. Supports both minimal demo and full research configurations.
"""

import os
import csv
import json
import wave
import struct
import argparse
import sys
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field, asdict
import logging

# TTS Libraries
try:
    from gtts import gTTS  # type: ignore
except Exception:
    gTTS = None  # Optional
try:
    import pyttsx3  # type: ignore
except Exception:
    pyttsx3 = None  # Optional
from pydub import AudioSegment
from pydub.generators import Sine

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class RecordingConfig:
    """Recording configuration parameters"""
    sample_rate: int = 44100  # Hz
    bit_depth: int = 16  # bits
    channels: int = 1  # mono
    target_db: float = -12.0  # dBFS
    silence_duration: int = 1000  # ms between recordings
    

@dataclass
class SpeakerMetadata:
    """Speaker information for metadata tracking"""
    speaker_id: str
    gender: str = "unknown"
    age: int = 0
    L1: str = "unknown"
    proficiency: str = "unknown"
    recording_date: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d"))
    mic_model: str = "TTS_synthesis"
    room: str = "digital"
    

@dataclass
class ExperimentConfig:
    """Experiment configuration"""
    mode: str = "minimal"  # "minimal" or "research"
    output_dir: str = "./audio_dataset"
    metadata_file: str = "metadata.csv"
    
    # Minimal configuration
    minimal_vowels: List[str] = field(default_factory=lambda: ["i", "a"])
    minimal_tokens_per_vowel: int = 5
    minimal_yn_questions: int = 5
    minimal_wh_questions: int = 5
    minimal_speakers: int = 3
    
    # Research configuration
    research_vowels: List[str] = field(default_factory=lambda: [
        "i", "ɪ", "e", "ɛ", "æ", "ʌ", "ɑ", "ɔ", "o", "ʊ", "u"
    ])
    research_tokens_per_vowel: int = 5
    research_cvc_words_per_vowel: int = 5
    research_repetitions: int = 2
    research_yn_questions: int = 10
    research_wh_questions: int = 10
    research_statements: int = 10
    research_speakers: int = 20


class AudioGenerator:
    """Main audio generation class"""
    
    def __init__(self, config: ExperimentConfig, recording_config: RecordingConfig):
        self.config = config
        self.recording_config = recording_config
        self.metadata_records = []
        
        # Create output directory structure
        self.setup_directories()
        
        # Initialize TTS engines
        self.setup_tts_engines()
        
    def setup_directories(self):
        """Create directory structure for output files"""
        self.base_dir = Path(self.config.output_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.dirs = {
            'sustained': self.base_dir / 'sustained_vowels',
            'words': self.base_dir / 'words',
            'sentences': self.base_dir / 'sentences',
            'metadata': self.base_dir / 'metadata'
        }
        
        for dir_path in self.dirs.values():
            dir_path.mkdir(exist_ok=True)
            
    def setup_tts_engines(self):
        """Initialize TTS engines"""
        # gTTS for basic generation
        self.gtts_lang = 'en'
        
        # pyttsx3 for more control
        try:
            self.pyttsx_engine = pyttsx3.init()
            self.pyttsx_engine.setProperty('rate', 150)  # Speech rate
            self.pyttsx_engine.setProperty('volume', 0.9)  # Volume
            
            # Try to set voice to English
            voices = self.pyttsx_engine.getProperty('voices')
            for voice in voices:
                if 'english' in voice.name.lower():
                    self.pyttsx_engine.setProperty('voice', voice.id)
                    break
        except:
            logger.warning("pyttsx3 initialization failed. Using gTTS only.")
            self.pyttsx_engine = None
    
    def generate_sustained_vowel(self, vowel: str, duration_ms: int = 2000) -> AudioSegment:
        """
        Generate sustained vowel sound using sine wave synthesis
        Note: This is a simplified approximation. Real vowel synthesis requires formant modeling.
        """
        # Vowel formant frequencies (F1, F2) - simplified approximations
        formants = {
            'i': (270, 2290),
            'ɪ': (390, 1990),
            'e': (530, 1840),
            'ɛ': (610, 1770),
            'æ': (690, 1660),
            'a': (710, 1220),
            'ʌ': (640, 1190),
            'ɑ': (710, 1100),
            'ɔ': (590, 880),
            'o': (470, 1020),
            'ʊ': (450, 1030),
            'u': (300, 870),
        }
        
        if vowel in formants:
            f1, f2 = formants[vowel]
            
            # Generate fundamental frequency (F0) - typical male voice
            f0 = 120  # Hz
            
            # Create composite sound with fundamental and formants
            sound = Sine(f0).to_audio_segment(duration=duration_ms)
            sound = sound.overlay(Sine(f1).to_audio_segment(duration=duration_ms) - 6)
            sound = sound.overlay(Sine(f2).to_audio_segment(duration=duration_ms) - 9)
            
            # Apply fade in/out for naturalness
            sound = sound.fade_in(100).fade_out(100)
            
            # Normalize to target dB
            sound = sound.apply_gain(self.recording_config.target_db - sound.dBFS)
            
            return sound
        else:
            # Fallback: use gTTS for unknown vowels
            return self.generate_with_gtts(vowel)
    
    def generate_with_gtts(self, text: str) -> AudioSegment:
        """Generate audio using gTTS"""
        temp_file = "temp_gtts.mp3"
        
        try:
            tts = gTTS(text=text, lang=self.gtts_lang, slow=False)
            tts.save(temp_file)
            
            # Load and convert to desired format
            sound = AudioSegment.from_mp3(temp_file)
            
            # Convert to mono
            if self.recording_config.channels == 1:
                sound = sound.set_channels(1)
            
            # Set sample rate
            sound = sound.set_frame_rate(self.recording_config.sample_rate)
            
            # Normalize volume
            sound = sound.apply_gain(self.recording_config.target_db - sound.dBFS)
            
            # Clean up temp file
            os.remove(temp_file)
            
            return sound
            
        except Exception as e:
            logger.error(f"gTTS generation failed: {e}")
            return AudioSegment.silent(duration=1000)
    
    def generate_cvc_word(self, vowel: str, word: str) -> AudioSegment:
        """Generate CVC word containing target vowel"""
        return self.generate_with_gtts(word)
    
    def generate_sentence(self, sentence: str, sentence_type: str) -> AudioSegment:
        """Generate sentence with appropriate intonation"""
        # For now, use gTTS. Advanced: modify pitch contour based on sentence_type
        return self.generate_with_gtts(sentence)
    
    def save_audio(self, audio: AudioSegment, filepath: Path, metadata: Dict):
        """Save audio file and record metadata"""
        # Export audio
        audio.export(
            filepath,
            format="wav",
            parameters=["-ar", str(self.recording_config.sample_rate)]
        )
        
        # Record metadata
        metadata['filepath'] = str(filepath)
        metadata['duration_ms'] = len(audio)
        metadata['sample_rate'] = self.recording_config.sample_rate
        metadata['bit_depth'] = self.recording_config.bit_depth
        self.metadata_records.append(metadata)
        
        logger.info(f"Saved: {filepath}")

    def emit_vowels(self, vowels: List[str], outdir: str = "data/audio",
                    duration_ms: int = 2000, tokens: int = 1,
                    sample_rate: Optional[int] = None,
                    prefix: str = "vowel") -> None:
        """Generate sustained vowels and write plain wav files into outdir.

        - Does not touch dataset metadata; intended for quick one-off assets
        - Uses simple synthesis via generate_sustained_vowel
        """
        out_path = Path(outdir)
        out_path.mkdir(parents=True, exist_ok=True)
        sr = sample_rate or self.recording_config.sample_rate

        for v in vowels:
            for rep in range(1, tokens + 1):
                audio = self.generate_sustained_vowel(vowel=v, duration_ms=duration_ms)
                # Enforce desired sample rate and channels
                audio = audio.set_frame_rate(sr)
                audio = audio.set_channels(self.recording_config.channels)
                if tokens == 1:
                    fname = f"{prefix}_{v}.wav"
                else:
                    fname = f"{prefix}_{v}_rep{rep:02d}.wav"
                fpath = out_path / fname
                audio.export(fpath, format="wav", parameters=["-ar", str(sr)])
                logger.info(f"Emitted {fpath}")
    
    def generate_minimal_dataset(self):
        """Generate minimal demonstration dataset"""
        logger.info("Generating minimal dataset...")
        
        # Sample sentences
        yn_questions = [
            "Is this a test?",
            "Do you like music?",
            "Can you hear me?",
            "Are you ready?",
            "Will it rain today?"
        ]
        
        wh_questions = [
            "What is your name?",
            "Where are you from?",
            "When will you arrive?",
            "Why is the sky blue?",
            "How does this work?"
        ]
        
        for speaker_num in range(1, self.config.minimal_speakers + 1):
            speaker = SpeakerMetadata(
                speaker_id=f"spk{speaker_num:03d}",
                gender="synthesized",
                age=0,
                L1="en",
                proficiency="native"
            )
            
            # Generate sustained vowels
            for vowel in self.config.minimal_vowels:
                for token_num in range(1, self.config.minimal_tokens_per_vowel + 1):
                    audio = self.generate_sustained_vowel(vowel, duration_ms=2000)
                    
                    filename = f"{speaker.speaker_id}_sustained_{vowel}_rep{token_num:02d}.wav"
                    filepath = self.dirs['sustained'] / filename
                    
                    metadata = asdict(speaker)
                    metadata.update({
                        'task': 'sustained_vowel',
                        'item': vowel,
                        'repetition': token_num
                    })
                    
                    self.save_audio(audio, filepath, metadata)
            
            # Generate Yes/No questions
            for idx, question in enumerate(yn_questions[:self.config.minimal_yn_questions], 1):
                for rep in range(1, 3):  # 2 repetitions
                    audio = self.generate_sentence(question, 'yn_question')
                    
                    filename = f"{speaker.speaker_id}_sent_yn_Q{idx:02d}_rep{rep:02d}.wav"
                    filepath = self.dirs['sentences'] / filename
                    
                    metadata = asdict(speaker)
                    metadata.update({
                        'task': 'sentence',
                        'sentence_type': 'yn_question',
                        'item': question,
                        'item_id': f"yn_Q{idx:02d}",
                        'repetition': rep
                    })
                    
                    self.save_audio(audio, filepath, metadata)
            
            # Generate WH questions
            for idx, question in enumerate(wh_questions[:self.config.minimal_wh_questions], 1):
                for rep in range(1, 3):  # 2 repetitions
                    audio = self.generate_sentence(question, 'wh_question')
                    
                    filename = f"{speaker.speaker_id}_sent_wh_Q{idx:02d}_rep{rep:02d}.wav"
                    filepath = self.dirs['sentences'] / filename
                    
                    metadata = asdict(speaker)
                    metadata.update({
                        'task': 'sentence',
                        'sentence_type': 'wh_question',
                        'item': question,
                        'item_id': f"wh_Q{idx:02d}",
                        'repetition': rep
                    })
                    
                    self.save_audio(audio, filepath, metadata)
    
    def generate_research_dataset(self):
        """Generate full research dataset"""
        logger.info("Generating research dataset...")
        
        # CVC words for each vowel (simplified examples)
        cvc_words = {
            'i': ['beat', 'seed', 'keep', 'team', 'lean'],
            'ɪ': ['bit', 'sit', 'kit', 'tip', 'lin'],
            'e': ['bait', 'sake', 'tape', 'main', 'late'],
            'ɛ': ['bet', 'set', 'kept', 'ten', 'let'],
            'æ': ['bat', 'sat', 'cat', 'tan', 'lap'],
            'ʌ': ['but', 'sun', 'cup', 'ton', 'luck'],
            'ɑ': ['pot', 'sock', 'cop', 'top', 'lock'],
            'ɔ': ['bought', 'sought', 'caught', 'taught', 'law'],
            'o': ['boat', 'soak', 'rope', 'tone', 'load'],
            'ʊ': ['book', 'took', 'cook', 'foot', 'look'],
            'u': ['boot', 'suit', 'soup', 'tool', 'loop']
        }
        
        # Extended sentence sets
        yn_questions = [
            "Is this a test?", "Do you like music?", "Can you hear me?",
            "Are you ready?", "Will it rain today?", "Have you seen the movie?",
            "Did you finish the work?", "Should we start now?", 
            "Could you help me?", "Would you like some tea?"
        ]
        
        wh_questions = [
            "What is your name?", "Where are you from?", "When will you arrive?",
            "Why is the sky blue?", "How does this work?", "Which one do you prefer?",
            "Who told you that?", "What time is it?", "Where did you go?",
            "How much does it cost?"
        ]
        
        statements = [
            "The weather is nice today.", "I like reading books.",
            "She plays the piano.", "They went to the park.",
            "The cat is sleeping.", "We need more time.",
            "He studies mathematics.", "The train arrives at noon.",
            "Coffee tastes bitter.", "Children love ice cream."
        ]
        
        # Generate for multiple speakers
        for speaker_num in range(1, min(self.config.research_speakers + 1, 6)):  # Limit for demo
            speaker = SpeakerMetadata(
                speaker_id=f"spk{speaker_num:03d}",
                gender="synthesized",
                age=0,
                L1="en",
                proficiency="native"
            )
            
            logger.info(f"Processing speaker {speaker.speaker_id}...")
            
            # Generate sustained vowels
            for vowel in self.config.research_vowels:
                for token_num in range(1, self.config.research_tokens_per_vowel + 1):
                    audio = self.generate_sustained_vowel(vowel, duration_ms=2000)
                    
                    filename = f"{speaker.speaker_id}_sustained_{vowel}_rep{token_num:02d}.wav"
                    filepath = self.dirs['sustained'] / filename
                    
                    metadata = asdict(speaker)
                    metadata.update({
                        'task': 'sustained_vowel',
                        'item': vowel,
                        'repetition': token_num
                    })
                    
                    self.save_audio(audio, filepath, metadata)
            
            # Generate CVC words
            for vowel, words in cvc_words.items():
                for word_idx, word in enumerate(words[:self.config.research_cvc_words_per_vowel], 1):
                    for rep in range(1, self.config.research_repetitions + 1):
                        audio = self.generate_cvc_word(vowel, word)
                        
                        filename = f"{speaker.speaker_id}_word_{word}_rep{rep:02d}.wav"
                        filepath = self.dirs['words'] / filename
                        
                        metadata = asdict(speaker)
                        metadata.update({
                            'task': 'cvc_word',
                            'target_vowel': vowel,
                            'item': word,
                            'repetition': rep
                        })
                        
                        self.save_audio(audio, filepath, metadata)
            
            # Generate sentences
            for sentence_type, sentences, prefix in [
                ('yn_question', yn_questions[:self.config.research_yn_questions], 'yn'),
                ('wh_question', wh_questions[:self.config.research_wh_questions], 'wh'),
                ('statement', statements[:self.config.research_statements], 'stmt')
            ]:
                for idx, sentence in enumerate(sentences, 1):
                    for rep in range(1, self.config.research_repetitions + 1):
                        audio = self.generate_sentence(sentence, sentence_type)
                        
                        filename = f"{speaker.speaker_id}_sent_{prefix}_S{idx:02d}_rep{rep:02d}.wav"
                        filepath = self.dirs['sentences'] / filename
                        
                        metadata = asdict(speaker)
                        metadata.update({
                            'task': 'sentence',
                            'sentence_type': sentence_type,
                            'item': sentence,
                            'item_id': f"{prefix}_S{idx:02d}",
                            'repetition': rep
                        })
                        
                        self.save_audio(audio, filepath, metadata)
    
    def save_metadata(self):
        """Save metadata to CSV file"""
        metadata_file = self.dirs['metadata'] / self.config.metadata_file
        
        if self.metadata_records:
            # Get all unique keys
            all_keys = set()
            for record in self.metadata_records:
                all_keys.update(record.keys())
            
            # Write CSV
            with open(metadata_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                writer.writeheader()
                writer.writerows(self.metadata_records)
            
            logger.info(f"Metadata saved to {metadata_file}")
    
    def generate_dataset_info(self):
        """Generate dataset information JSON file"""
        info = {
            'dataset_name': 'English Phonetic Research Dataset',
            'creation_date': datetime.now().isoformat(),
            'configuration': asdict(self.config),
            'recording_config': asdict(self.recording_config),
            'total_files': len(self.metadata_records),
            'file_types': {
                'sustained_vowels': len([r for r in self.metadata_records if r.get('task') == 'sustained_vowel']),
                'cvc_words': len([r for r in self.metadata_records if r.get('task') == 'cvc_word']),
                'sentences': len([r for r in self.metadata_records if r.get('task') == 'sentence'])
            }
        }
        
        info_file = self.dirs['metadata'] / 'dataset_info.json'
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Dataset info saved to {info_file}")
    
    def run(self):
        """Execute dataset generation"""
        logger.info(f"Starting audio generation in {self.config.mode} mode...")
        
        if self.config.mode == 'minimal':
            self.generate_minimal_dataset()
        elif self.config.mode == 'research':
            self.generate_research_dataset()
        else:
            raise ValueError(f"Unknown mode: {self.config.mode}")
        
        # Save metadata and info
        self.save_metadata()
        self.generate_dataset_info()
        
        logger.info(f"Dataset generation complete! Total files: {len(self.metadata_records)}")
        logger.info(f"Output directory: {self.base_dir}")


def interactive_main():
    """Interactive execution fallback when no CLI flags are provided"""
    print("English Audio Dataset Generator")
    print("=" * 50)
    print("Select mode:")
    print("1. Minimal (quick demo)")
    print("2. Research (comprehensive)")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == '1':
        mode = 'minimal'
        print("\nGenerating minimal dataset...")
    elif choice == '2':
        mode = 'research'
        print("\nGenerating research dataset (this may take a while)...")
    else:
        print("Invalid choice. Using minimal mode.")
        mode = 'minimal'

    experiment_config = ExperimentConfig(mode=mode)
    recording_config = RecordingConfig()

    generator = AudioGenerator(experiment_config, recording_config)
    generator.run()

    print("\n" + "=" * 50)
    print("Dataset generation complete!")
    print(f"Files saved to: {experiment_config.output_dir}")
    print("\nNext steps:")
    print("1. Review generated audio files")
    print("2. Check metadata.csv for file information")
    print("3. Use Praat/ELAN for annotation")
    print("4. Extract acoustic features (F0, F1/F2)")
    print("5. Proceed with statistical analysis (GLMM)")


def cli_main(argv=None):
    """CLI entrypoint supporting vowel emission and dataset generation."""
    parser = argparse.ArgumentParser(description="English Audio Dataset Generator")
    parser.add_argument("--mode", choices=["minimal", "research"], default=None,
                        help="Non-interactive dataset generation mode")
    parser.add_argument("--emit-vowels", nargs="+", dest="emit_vowels",
                        help="Emit sustained vowels into a target directory (e.g., i a u)")
    parser.add_argument("--outdir", default="data/audio", help="Output directory for emitted vowels")
    parser.add_argument("--duration-ms", type=int, default=2000, help="Duration per vowel token in ms")
    parser.add_argument("--tokens", type=int, default=1, help="Number of tokens per vowel")
    parser.add_argument("--sample-rate", type=int, default=16000, help="Sample rate for emitted WAVs")

    args = parser.parse_args(argv)

    # Emit quick vowels (one-off assets)
    if args.emit_vowels:
        experiment_config = ExperimentConfig(mode="minimal")
        recording_config = RecordingConfig(sample_rate=args.sample_rate)
        generator = AudioGenerator(experiment_config, recording_config)
        generator.emit_vowels(args.emit_vowels, outdir=args.outdir,
                              duration_ms=args.duration_ms, tokens=args.tokens,
                              sample_rate=args.sample_rate)
        return 0

    # Non-interactive dataset generation
    if args.mode:
        experiment_config = ExperimentConfig(mode=args.mode)
        recording_config = RecordingConfig()
        generator = AudioGenerator(experiment_config, recording_config)
        generator.run()
        return 0

    # Fallback to interactive mode
    interactive_main()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(cli_main())
    except KeyboardInterrupt:
        print("\n\nGeneration interrupted by user.")
    except Exception as e:
        logger.error(f"Error during generation: {e}")
        raise
