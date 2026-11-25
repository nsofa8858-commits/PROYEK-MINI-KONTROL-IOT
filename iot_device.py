
import time
import random
import json
import paho.mqtt.client as mqtt

# ==========================================
# 1. KONFIGURASI MQTT
# ==========================================

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "PythonDevice-001"

# NIM: 2410020094
TOPIC_SUHU = "iot/2410020094/sensor/suhu"
TOPIC_RELAY = "iot/2410020094/aktuator/relay"
TOPIC_PWM = "iot/2410020094/aktuator/pwm"

# ==========================================
# 2. STATUS PERANGKAT (SIMULASI LAPTOP)
# ==========================================

relay_status = "OFF"
led_brightness = 0

# ==========================================
# 3. KETIKA BERHASIL TERHUBUNG MQTT
# ==========================================

def on_connect(client, userdata, flags, reason_code, properties):
    print("\n===================================")
    print(" BERHASIL TERHUBUNG KE MQTT BROKER")
    print("===================================")

    print("Broker :", MQTT_BROKER)
    print("Port   :", MQTT_PORT)

    # Berlangganan topik relay dan PWM
    client.subscribe(TOPIC_RELAY)
    client.subscribe(TOPIC_PWM)

    print("\nMenunggu perintah dari Node-RED...")
    print("===================================\n")


# ==========================================
# 4. MENERIMA PESAN DARI NODE-RED
# ==========================================

def on_message(client, userdata, message):

    global relay_status
    global led_brightness

    topic = message.topic
    payload = message.payload.decode("utf-8").strip()

    # --------------------------------------
    # KONTROL RELAY
    # --------------------------------------

    if topic == TOPIC_RELAY:

        perintah = payload.upper()

        if perintah == "ON":
            relay_status = "ON"

            print("\n[RELAY] LAMPU DINYALAKAN")
            print("Status Relay :", relay_status)

        elif perintah == "OFF":
            relay_status = "OFF"

            print("\n[RELAY] LAMPU DIMATIKAN")
            print("Status Relay :", relay_status)

        else:
            print("[ERROR] Perintah relay tidak dikenal:", payload)

    # --------------------------------------
    # KONTROL KECERAHAN LED
    # --------------------------------------

    elif topic == TOPIC_PWM:

        try:
            nilai = int(float(payload))

            if 0 <= nilai <= 255:

                led_brightness = nilai

                persen = round((nilai / 255) * 100, 1)

                print("\n[LED] Kecerahan diperbarui")
                print("Nilai PWM :", led_brightness)
                print("Kecerahan :", persen, "%")

            else:
                print("[ERROR] Nilai PWM harus 0 sampai 255")

        except ValueError:
            print("[ERROR] Data PWM bukan angka:", payload)


# ==========================================
# 5. MEMBUAT KONEKSI MQTT
# ==========================================

client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id=MQTT_CLIENT_ID
)

client.on_connect = on_connect
client.on_message = on_message


# ==========================================
# 6. MENGHUBUNGKAN KE BROKER
# ==========================================

try:

    print("===================================")
    print("       PYTHON IOT DEVICE")
    print("===================================")

    print("Menghubungkan ke MQTT Broker...")

    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Menjalankan koneksi MQTT di background
    client.loop_start()

    # Tunggu koneksi selesai
    time.sleep(2)

    # ======================================
    # 7. MENGIRIM DATA SUHU SETIAP 3 DETIK
    # ======================================

    while True:

        # Simulasi pembacaan sensor DHT22
        suhu = round(random.uniform(25.0, 35.0), 1)

        kelembaban = round(random.uniform(50.0, 85.0), 1)

        # Data sensor dalam format JSON
        data_sensor = {
            "suhu": suhu,
            "kelembaban": kelembaban
        }

        # Kirim nilai suhu ke Node-RED
        hasil = client.publish(
            TOPIC_SUHU,
            str(suhu),
            qos=0
        )

        print("\n========== DATA SENSOR ==========")
        print("Suhu       :", suhu, "°C")
        print("Kelembaban :", kelembaban, "%")
        print("Topik      :", TOPIC_SUHU)
        print("Status     : Data dikirim")
        print("=================================")

        time.sleep(3)


except KeyboardInterrupt:

    print("\nProgram dihentikan oleh pengguna.")

except Exception as error:

    print("\nTerjadi kesalahan:", error)

finally:

    client.loop_stop()
    client.disconnect()

    print("Koneksi MQTT diputus.")
    print("Program selesai.")
