#!/usr/bin/env python
"""
Generate a new Django SECRET_KEY for production use.
Run this script and copy the output to your .env file.
"""

from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    print("=" * 70)
    print("Django SECRET_KEY Generator")
    print("=" * 70)
    print("\nYour new SECRET_KEY:")
    print("-" * 70)
    print(get_random_secret_key())
    print("-" * 70)
    print("\nCopy the key above and paste it in your .env file:")
    print("SECRET_KEY=your-generated-key-here")
    print("\nIMPORTANT: Keep this key secret and never commit it to version control!")
    print("=" * 70)