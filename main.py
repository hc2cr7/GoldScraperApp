from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
import gold_scraper # Your scraper script

class GridSlayerApp(App):
    def build(self):
        Clock.schedule_interval(lambda dt: gold_scraper.main(), 300) 
        return Label(text="Gold Scraper is cooking... 🍳🚀")

if __name__ == '__main__':
    GridSlayerApp().run()
