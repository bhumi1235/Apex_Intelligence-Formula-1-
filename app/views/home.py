import streamlit as st

from components.navbar import render_navbar
from components.hero import render_hero
from components.race_card import render_race_card
from components.prediction_cards import render_prediction_cards


def show_home():

    render_navbar()

    render_hero()

    render_race_card()

    render_prediction_cards()