from flask import render_template, request, redirect, url_for
from app import app
import os


@app.route('/')
def create_note():
    return render_template('create_note.html')
