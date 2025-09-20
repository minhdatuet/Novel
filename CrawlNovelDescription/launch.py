#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SangTacViet Crawler Launcher
Cho phép chọn chạy GUI hoặc CLI
"""

import sys
import os

def main():
    print("=" * 50)
    print("  🕸️ SANGTACVIET NOVEL CRAWLER")
    print("=" * 50)
    print()
    print("Chọn phiên bản để chạy:")
    print("1. 🖥️  GUI Version (Giao diện đồ họa)")
    print("2. 💻  CLI Version (Dòng lệnh)")
    print("0. ❌  Thoát")
    print()
    
    while True:
        choice = input("Nhập lựa chọn (0-2): ").strip()
        
        if choice == '0':
            print("👋 Tạm biệt!")
            sys.exit(0)
        
        elif choice == '1':
            print("\n🖥️ Khởi động GUI Version...")
            try:
                os.system("python sangtacviet_gui.py")
            except KeyboardInterrupt:
                print("\n👋 GUI đã đóng!")
            break
        
        elif choice == '2':
            print("\n💻 Khởi động CLI Version...")
            try:
                os.system("python sangtacviet_final_crawler.py")
            except KeyboardInterrupt:
                print("\n👋 CLI đã đóng!")
            break
        
        else:
            print("❌ Lựa chọn không hợp lệ! Vui lòng nhập 0, 1 hoặc 2.")

if __name__ == "__main__":
    main()
