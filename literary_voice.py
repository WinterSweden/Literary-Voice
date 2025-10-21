#!/usr/bin/env python3
"""
The Literary Voice CLI
A Goodreads-powered book recommendation assistant
"""

import requests
import time
import sys
import json
import os
from pathlib import Path
import re
from bs4 import BeautifulSoup

# Configuration
CONFIG_DIR = Path.home() / ".literary-voice"
CONFIG_FILE = CONFIG_DIR / "config.json"
API_BASE_URL = "http://localhost:5000"  # Change to Railway URL after deployment

class LiteraryVoice:
    def __init__(self):
        self.api_key = None
        self.email = None
        self.load_config()
    
    def load_config(self):
        """Load saved API key from config file"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.api_key = config.get('api_key')
                self.email = config.get('email')
    
    def save_config(self, api_key, email):
        """Save API key to config file"""
        CONFIG_DIR.mkdir(exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'api_key': api_key, 'email': email}, f)
        self.api_key = api_key
        self.email = email
    
    def clear_config(self):
        """Clear saved config (logout)"""
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
        self.api_key = None
        self.email = None
    
    def type_text(self, text, delay=0.02):
        """Print text with typing effect"""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()
    
    def print_header(self):
        """Print the Literary Voice header"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print("\n" + "="*50)
        print("           The Literary Voice")
        print("        Your AI Reading Companion")
        print("="*50 + "\n")
    
    def login(self):
        """Login existing user"""
        self.print_header()
        print("🔐 Login\n")
        
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        
        try:
            response = requests.post(f"{API_BASE_URL}/login", json={
                'email': email,
                'password': password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.save_config(data['api_key'], email)
                print("\n✅ Login successful!")
                time.sleep(1)
                return True
            else:
                print(f"\n❌ {response.json().get('error', 'Login failed')}")
                time.sleep(2)
                return False
        except Exception as e:
            print(f"\n❌ Connection error: {e}")
            time.sleep(2)
            return False
    
    def signup(self):
        """Register new user"""
        self.print_header()
        print("✨ Sign Up\n")
        
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        confirm = input("Confirm Password: ").strip()
        
        if password != confirm:
            print("\n❌ Passwords don't match!")
            time.sleep(2)
            return False
        
        try:
            response = requests.post(f"{API_BASE_URL}/signup", json={
                'email': email,
                'password': password
            })
            
            if response.status_code == 201:
                data = response.json()
                self.save_config(data['api_key'], email)
                print("\n✅ Account created successfully!")
                print(f"You have {data['credits']} credits to start.")
                time.sleep(2)
                return True
            else:
                print(f"\n❌ {response.json().get('error', 'Signup failed')}")
                time.sleep(2)
                return False
        except Exception as e:
            print(f"\n❌ Connection error: {e}")
            time.sleep(2)
            return False
    
    def auth_menu(self):
        """Show login/signup menu"""
        while True:
            self.print_header()
            print("[1] 🔐 Login")
            print("[2] ✨ Sign Up")
            print("[3] ❌ Exit\n")
            
            choice = input("> ").strip()
            
            if choice == '1':
                if self.login():
                    return True
            elif choice == '2':
                if self.signup():
                    return True
            elif choice == '3':
                print("\nGoodbye! 📚")
                return False
            else:
                print("\n❌ Invalid choice!")
                time.sleep(1)
    
    def get_balance(self):
        """Check credit balance"""
        try:
            response = requests.get(f"{API_BASE_URL}/balance", headers={
                'X-API-Key': self.api_key
            })
            
            if response.status_code == 200:
                return response.json()['credits']
            return None
        except:
            return None
    
    def detect_input_type(self, user_input):
        """Detect if input is ISBN or book title"""
        # Remove hyphens and spaces
        cleaned = user_input.replace('-', '').replace(' ', '')
        
        # ISBN-10 or ISBN-13
        if cleaned.isdigit() and (len(cleaned) == 10 or len(cleaned) == 13):
            return 'isbn', user_input
        
        return 'title', user_input
    
    def search_goodreads(self, query, input_type):
        """Search for book on Goodreads"""
        print("\n🔍 Searching Goodreads...")
        time.sleep(0.5)  # Rate limiting
        
        try:
            if input_type == 'isbn':
                search_url = f"https://www.goodreads.com/search?q={query}&search_type=books"
            else:
                search_url = f"https://www.goodreads.com/search?q={query.replace(' ', '+')}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find first book result
            book_link = soup.find('a', class_='bookTitle')
            if not book_link:
                return None
            
            book_url = 'https://www.goodreads.com' + book_link['href']
            book_title = book_link.text.strip()
            
            # Get author
            author_link = soup.find('a', class_='authorName')
            author = author_link.text.strip() if author_link else "Unknown"
            
            return {
                'title': book_title,
                'author': author,
                'url': book_url
            }
        except Exception as e:
            print(f"Error searching: {e}")
            return None
    
    def scrape_reviews(self, book_url):
        """Scrape top reviews from Goodreads"""
        print("📖 Analyzing reviews...")
        time.sleep(1)  # Rate limiting
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(book_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            reviews = []
            review_elements = soup.find_all('div', class_='review', limit=5)
            
            for review in review_elements:
                # Get review text
                text_elem = review.find('span', class_='readable')
                if not text_elem:
                    continue
                
                text = text_elem.get_text(strip=True)
                
                # Get likes count
                likes_elem = review.find('span', class_='likesCount')
                likes = 0
                if likes_elem:
                    likes_text = likes_elem.get_text()
                    nums = re.findall(r'\d+', likes_text)
                    likes = int(nums[0]) if nums else 0
                
                reviews.append({
                    'text': text,
                    'likes': likes
                })
            
            if not reviews:
                return None
            
            # Return most liked review
            return max(reviews, key=lambda x: x['likes'])
        except Exception as e:
            print(f"Error scraping reviews: {e}")
            return None
    
    def reformat_review(self, review_text, book_title, author):
        """Simple rule-based review reformatting"""
        # Split into sentences
        sentences = [s.strip() + '.' for s in review_text.split('.') if s.strip()]
        
        # Categorize sentences
        positive_keywords = ['love', 'great', 'amazing', 'perfect', 'best', 'wonderful', 
                           'excellent', 'brilliant', 'beautiful', 'favorite', 'enjoyed']
        negative_keywords = ['hate', 'bad', 'worst', 'boring', 'disappointed', 'poor',
                           'terrible', 'awful', 'waste', 'slow']
        
        positive = []
        negative = []
        neutral = []
        
        for sentence in sentences:
            lower = sentence.lower()
            if any(word in lower for word in positive_keywords):
                positive.append(sentence)
            elif any(word in lower for word in negative_keywords):
                negative.append(sentence)
            else:
                neutral.append(sentence)
        
        # Build output
        output = f"\n{'='*60}\n"
        output += f"What readers think about '{book_title}' by {author}\n"
        output += f"{'='*60}\n\n"
        
        if positive:
            output += "✨ The Highlights:\n\n"
            for point in positive[:3]:
                output += f"  • {point}\n"
            output += "\n"
        
        if negative:
            output += "⚠️  Some Considerations:\n\n"
            for point in negative[:2]:
                output += f"  • {point}\n"
            output += "\n"
        
        if neutral:
            output += "📝 Overall Perspective:\n\n"
            output += f"  {neutral[0]}\n\n"
        elif positive:
            output += "📝 Overall Perspective:\n\n"
            output += f"  {positive[0]}\n\n"
        
        output += f"{'='*60}\n"
        
        return output
    
    def get_book_info(self, book_data):
        """Get book information"""
        output = f"\n{'='*60}\n"
        output += f"📚 {book_data['title']}\n"
        output += f"✍️  by {book_data['author']}\n"
        output += f"🔗 {book_data['url']}\n"
        output += f"{'='*60}\n"
        return output
    
    def get_author_books(self, author_name):
        """Get books by author from Goodreads"""
        print(f"\n🔍 Finding books by {author_name}...")
        time.sleep(1)
        
        try:
            search_url = f"https://www.goodreads.com/search?q={author_name.replace(' ', '+')}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            books = []
            results = soup.find_all('tr', itemtype='http://schema.org/Book', limit=10)
            
            for result in results:
                title_elem = result.find('a', class_='bookTitle')
                rating_elem = result.find('span', class_='minirating')
                
                if title_elem:
                    title = title_elem.text.strip()
                    rating = rating_elem.text.strip() if rating_elem else "No rating"
                    books.append({'title': title, 'rating': rating})
            
            output = f"\n{'='*60}\n"
            output += f"📚 Books by {author_name}\n"
            output += f"{'='*60}\n\n"
            
            for i, book in enumerate(books, 1):
                output += f"{i}. {book['title']}\n"
                output += f"   ⭐ {book['rating']}\n\n"
            
            output += f"{'='*60}\n"
            return output
        except Exception as e:
            return f"\n❌ Error finding books: {e}\n"
    
    def deduct_credits(self, amount, action):
        """Deduct credits from user account"""
        try:
            response = requests.post(f"{API_BASE_URL}/deduct", 
                json={'amount': amount, 'action': action},
                headers={'X-API-Key': self.api_key}
            )
            return response.status_code == 200
        except:
            return False
    
    def main_menu(self):
        """Main application menu"""
        while True:
            self.print_header()
            
            balance = self.get_balance()
            if balance is not None:
                print(f"💎 Balance: {balance} credits | 👤 {self.email}\n")
            
            print("[1] 📖 Get Review")
            print("[2] ℹ️  Book Information")
            print("[3] 📚 Similar Books")
            print("[4] 💳 Check Balance")
            print("[5] ⬆️  Upgrade Plan")
            print("[6] 🚪 Logout")
            print("[7] ❌ Exit\n")
            
            choice = input("> ").strip()
            
            if choice == '1':
                self.handle_review()
            elif choice == '2':
                self.handle_info()
            elif choice == '3':
                self.handle_similar()
            elif choice == '4':
                self.handle_balance()
            elif choice == '5':
                self.handle_upgrade()
            elif choice == '6':
                self.clear_config()
                print("\n👋 Logged out successfully!")
                time.sleep(1)
                return
            elif choice == '7':
                print("\nGoodbye! Happy reading! 📚")
                sys.exit(0)
            else:
                print("\n❌ Invalid choice!")
                time.sleep(1)
    
    def handle_review(self):
        """Handle review request"""
        self.print_header()
        print("📖 Get Review\n")
        
        query = input("Enter book title or ISBN: ").strip()
        if not query:
            return
        
        input_type, cleaned_query = self.detect_input_type(query)
        
        # Search book
        book_data = self.search_goodreads(cleaned_query, input_type)
        if not book_data:
            print("\n❌ Book not found!")
            time.sleep(2)
            return
        
        # Scrape reviews
        review = self.scrape_reviews(book_data['url'])
        if not review:
            print("\n❌ No reviews found! Refunding credits...")
            time.sleep(2)
            return
        
        # Deduct credits
        if not self.deduct_credits(5, 'review'):
            print("\n❌ Insufficient credits!")
            time.sleep(2)
            return
        
        # Reformat and display
        reformatted = self.reformat_review(review['text'], book_data['title'], book_data['author'])
        
        self.print_header()
        self.type_text(reformatted, delay=0.01)
        
        input("\n\nPress Enter to continue...")
    
    def handle_info(self):
        """Handle book information request"""
        self.print_header()
        print("ℹ️  Book Information\n")
        
        query = input("Enter book title or ISBN: ").strip()
        if not query:
            return
        
        input_type, cleaned_query = self.detect_input_type(query)
        
        # Search book
        book_data = self.search_goodreads(cleaned_query, input_type)
        if not book_data:
            print("\n❌ Book not found!")
            time.sleep(2)
            return
        
        # Deduct credits
        if not self.deduct_credits(1, 'info'):
            print("\n❌ Insufficient credits!")
            time.sleep(2)
            return
        
        # Display info
        info = self.get_book_info(book_data)
        
        self.print_header()
        self.type_text(info, delay=0.01)
        
        input("\n\nPress Enter to continue...")
    
    def handle_similar(self):
        """Handle similar books request"""
        self.print_header()
        print("📚 Similar Books (by same author)\n")
        
        query = input("Enter book title or author name: ").strip()
        if not query:
            return
        
        # Try to find author
        input_type, cleaned_query = self.detect_input_type(query)
        book_data = self.search_goodreads(cleaned_query, input_type)
        
        if book_data:
            author = book_data['author']
        else:
            author = query
        
        # Deduct credits
        if not self.deduct_credits(2, 'similar'):
            print("\n❌ Insufficient credits!")
            time.sleep(2)
            return
        
        # Get author books
        books = self.get_author_books(author)
        
        self.print_header()
        self.type_text(books, delay=0.01)
        
        input("\n\nPress Enter to continue...")
    
    def handle_balance(self):
        """Handle balance check"""
        self.print_header()
        balance = self.get_balance()
        
        if balance is not None:
            print(f"\n💎 Current Balance: {balance} credits\n")
            print("Credit costs:")
            print("  • Review: 5 credits")
            print("  • Information: 1 credit")
            print("  • Similar Books: 2 credits\n")
        else:
            print("\n❌ Could not fetch balance!\n")
        
        input("Press Enter to continue...")
    
    def handle_upgrade(self):
        """Handle upgrade information"""
        self.print_header()
        print("\n⬆️  Upgrade Your Plan\n")
        print("="*60)
        print("\n📦 Commoner (FREE)")
        print("   • 15 credits/month")
        print("   • ~3 reviews per month\n")
        print("👑 Noble ($3/month)")
        print("   • 250 credits/month")
        print("   • ~50 reviews per month\n")
        print("💎 Royal ($9/month)")
        print("   • 1000 credits/month")
        print("   • ~200 reviews per month\n")
        print("="*60)
        print("\nVisit: https://literaryvoice.com/upgrade")
        print("(Manual payment processing during beta)\n")
        
        input("Press Enter to continue...")
    
    def run(self):
        """Main application entry point"""
        try:
            # Check if already logged in
            if self.api_key:
                self.main_menu()
            else:
                if self.auth_menu():
                    self.main_menu()
        except KeyboardInterrupt:
            print("\n\nGoodbye! 📚")
            sys.exit(0)

if __name__ == "__main__":
    app = LiteraryVoice()
    app.run()
