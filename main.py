import re
import json
from PyPDF2 import PdfReader
import tkinter as tk
from tkinter import scrolledtext

plants = []

def baca_pdf(file_pdf):
    try:
        reader = PdfReader(file_pdf)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        if text:
            print(f"PDF berhasil dibaca. Jumlah karakter: {len(text)}")
            return text
        else:
            print("PDF tidak berisi teks.")
            return None
    except Exception as e:
        print(f"Terjadi kesalahan saat membaca PDF: {e}")
        return None

def preprocessing_teks(teks):
    teks = re.sub(r'\s+', ' ', teks)
    return teks


def extract_data(text):
    if not text:
        print("Tidak ada teks untuk diekstraksi.")
        return []

    text = preprocessing_teks(text)

    pattern_tanaman = r'\d+\.\s*Nama Tanaman\s*:\s*(.*?),\s*Ketinggian Tempat \(mdpl\)\s*:\s*(.*?),\s*Curah Hujan\s*\(mm/bulan\)\s*:\s*(.*?),\s*Bulan Tanam\s*:\s*(.*?)(?:;|$)'
    matches_tanaman = re.findall(pattern_tanaman, text)

    plants_list = []
    for match in matches_tanaman:
        plant = {
            "nama_tanaman": match[0].strip(),
            "ketinggian_tempat": match[1].strip(),
            "curah_hujan": match[2].strip(),
            "bulan_tanam": [bulan.strip() for bulan in match[3].split(',')]
        }
        plants_list.append(plant)

    return plants_list



def extract_rules(plants):
    rules = []
    for i, plant in enumerate(plants, 1):
        rule = f"Rule {i}: Tanaman {plant['nama_tanaman']} dapat ditanam di ketinggian {plant['ketinggian_tempat']} mdpl " \
               f"dengan curah hujan {plant['curah_hujan']} mm/bulan pada bulan {', '.join(plant['bulan_tanam'])}."
        rules.append(rule)
    return rules


def cek_rekomendasi(plants, ketinggian, curah_hujan, bulan):
    rekomendasi = []
    alternatif = []

    for plant in plants:
        min_ketinggian, max_ketinggian = map(int, plant['ketinggian_tempat'].split(' - '))
        min_curah_hujan, max_curah_hujan = map(int, plant['curah_hujan'].split(' - '))

        if min_ketinggian <= ketinggian <= max_ketinggian and min_curah_hujan <= curah_hujan <= max_curah_hujan and bulan in \
                plant['bulan_tanam']:
            rekomendasi.append(plant['nama_tanaman'])
        elif (min_ketinggian - 200) <= ketinggian <= (max_ketinggian + 200) and (
                min_curah_hujan - 50) <= curah_hujan <= (max_curah_hujan + 50):
            alternatif.append(plant['nama_tanaman'])

    if rekomendasi:
        return f"Tanaman yang direkomendasikan: {', '.join(rekomendasi)}"

    if alternatif:
        return f"Tidak ada tanaman yang cocok.\nAlternatif: {', '.join(alternatif)}"

    return "Tidak ada tanaman yang cocok dengan input tersebut."

def input_dari_pengguna(plants):
    print("\nMasukkan data untuk mendapatkan rekomendasi tanaman:")
    ketinggian = int(input("Masukkan Ketinggian Tempat (mdpl): "))
    curah_hujan = int(input("Masukkan Curah Hujan (mm/bulan): "))
    bulan = input("Masukkan Bulan Tanam: ").capitalize()  # Contoh: April, Mei, dst.

    hasil = cek_rekomendasi(plants, ketinggian, curah_hujan, bulan)
    print(hasil)



def tampilkan_teks_window(teks, plants):
    root = tk.Tk()
    root.title("Hasil Pembacaan PDF")

    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=30)
    text_area.pack(padx=10, pady=10)

    text_area.insert(tk.INSERT, teks)

    text_area.configure(state='disabled')

    tk.Button(root, text="Buka Rekomendasi Tanaman", command=lambda: buka_rekomendasi_gui(plants)).pack(pady=10)

    root.mainloop()



def buka_rekomendasi_gui(plants):
    rekomendasi_window = tk.Tk()
    rekomendasi_window.title("Rekomendasi Tanaman")

    label_ketinggian = tk.Label(rekomendasi_window, text="Masukkan Ketinggian Tempat (mdpl):")
    label_ketinggian.pack(pady=5)
    entry_ketinggian = tk.Entry(rekomendasi_window)
    entry_ketinggian.pack(pady=5)

    label_curah_hujan = tk.Label(rekomendasi_window, text="Masukkan Curah Hujan (mm/bulan):")
    label_curah_hujan.pack(pady=5)
    entry_curah_hujan = tk.Entry(rekomendasi_window)
    entry_curah_hujan.pack(pady=5)

    label_bulan = tk.Label(rekomendasi_window, text="Masukkan Bulan Tanam:")
    label_bulan.pack(pady=5)
    entry_bulan = tk.Entry(rekomendasi_window)
    entry_bulan.pack(pady=5)

    def cek_rekomendasi_button():
        try:
            ketinggian = int(entry_ketinggian.get())
            curah_hujan = int(entry_curah_hujan.get())
            bulan = entry_bulan.get().capitalize()

            hasil_rekomendasi = cek_rekomendasi(plants, ketinggian, curah_hujan, bulan)
            result_label.config(text=hasil_rekomendasi)
        except ValueError:
            result_label.config(text="Input tidak valid. Silakan masukkan angka yang benar.")

    tk.Button(rekomendasi_window, text="Cek Rekomendasi", command=cek_rekomendasi_button).pack(pady=10)
    result_label = tk.Label(rekomendasi_window, text="")
    result_label.pack(pady=10)

    rekomendasi_window.mainloop()



def format_output(plants, rules):
    output = "Data Tanaman:\n"
    for i, plant in enumerate(plants, 1):
        output += f"{i}. Nama Tanaman: {plant['nama_tanaman']}, Ketinggian Tempat (mdpl): {plant['ketinggian_tempat']}, " \
                  f"Curah Hujan(mm/bulan): {plant['curah_hujan']}, Bulan Tanam: {', '.join(plant['bulan_tanam'])}\n"

    output += "\nRULE:\n"
    for i, rule in enumerate(rules, 1):
        output += f"{i}. {rule}\n"

    return output



def main():
    global plants
    file_pdf = 'data_tugas2.pdf'
    text_pdf = baca_pdf(file_pdf)

    if text_pdf:
        plants = extract_data(text_pdf)

        if plants:
            rules = extract_rules(plants)
            output = format_output(plants, rules)
            tampilkan_teks_window(output, plants)

            data_output = {
                "plants": plants,
                "rules": rules
            }
            with open('data_tanaman.json', 'w') as json_file:
                json.dump(data_output, json_file, indent=4)
            print("Data berhasil disimpan ke data_tanaman.json")
        else:
            print("Tidak ada data tanaman yang ditemukan.")
    else:
        print("Gagal membaca PDF atau PDF kosong.")


if __name__ == "__main__":
    main()
