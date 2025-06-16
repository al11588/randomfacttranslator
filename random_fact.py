import requests
import json
from datetime import datetime
from deep_translator import GoogleTranslator
import sqlite3
import pandas as pd

def setup_database():
    #Create our database and table if they don't exist yet
    conn = sqlite3.connect('facts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            english_fact TEXT,
            translated_fact TEXT,
            target_language TEXT
        )
    ''')
    conn.commit()
    return conn

def save_fact(conn, date, english_fact, translated_fact, target_lang):
    #Save the fact and its translation to our database
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO facts (date, english_fact, translated_fact, target_language)
        VALUES (?, ?, ?, ?)
    ''', (date, english_fact, translated_fact, target_lang))
    conn.commit()

def export_facts(conn):
    #Export all saved facts to a CSV file
    df = pd.read_sql_query("SELECT * FROM facts", conn)
    filename = f"facts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    return filename

def translate_fact(text, target_lang):
    # Translate the fact to the selected language
    try:
        translator = GoogleTranslator(source='en', target=target_lang)
        return translator.translate(text)
    except Exception as e:
        return f"Oops! Translation failed: {str(e)}"

def get_random_fact():
    # Main function to get and handle random facts
    url = "https://uselessfacts.jsph.pl/api/v2/facts/random"
    
    try:
        # Set up our database
        conn = setup_database()
        
        # Get a random fact
        response = requests.get(url)
        response.raise_for_status()
        
        fact_data = response.json()
        english_fact = fact_data['text']
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Show the fact
        print("\nRandom Fact of the Day")
        print(f"Date: {current_date}")
        print(f"\nFact: {english_fact}")
        
        while True:
            print("\nWhat would you like to do?")
            print("1. Translate this fact")
            print("2. Export all saved facts to CSV")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == "1":
                print("\nPick a language:")
                print("1. Spanish")
                print("2. French")
                print("3. Italian")
                print("4. Arabic")
                
                lang_choice = input("\nWhich language? (1-4): ")
                
                languages = {
                    "1": "es",
                    "2": "fr",
                    "3": "it",
                    "4": "ar"
                }
                
                if lang_choice in languages:
                    translated_fact = translate_fact(english_fact, languages[lang_choice])
                    print(f"\nTranslated Fact: {translated_fact}")
                    
                    if input("\nWant to save this fact? (y/n): ").lower() == 'y':
                        save_fact(conn, current_date, english_fact, translated_fact, languages[lang_choice])
                        print("Saved!")
                else:
                    print("\nThat's not a valid language choice!")
                    
            elif choice == "2":
                try:
                    filename = export_facts(conn)
                    print(f"\nAll facts exported to {filename}")
                except Exception as e:
                    print(f"\nCouldn't export facts: {e}")
                    
            elif choice == "3":
                print("\nSee you later!")
                break
            else:
                print("\nPlease pick 1, 2, or 3!")
        
    except requests.exceptions.RequestException as e:
        print(f"Couldn't get a fact: {e}")
    except json.JSONDecodeError:
        print("Something went wrong with the fact data")
    except Exception as e:
        print(f"Oops! Something unexpected happened: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    get_random_fact() 