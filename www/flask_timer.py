from flask import Flask, jsonify, render_template_string
import threading
import relay
import serial

app = Flask(__name__)
data_queue = relay.data_queue

# Shared state
start_time = None
stop_time = None
formatted_time = "0:00:000"

@app.route("/timer")
def get_timer_info():
    global start_time, stop_time, formatted_time

    while not data_queue.empty():
        event = data_queue.get()
        if event['event'] == 'START':
            start_time = event['timestamp']
            stop_time = None
        elif event['event'] == 'STOP':
            stop_time = event['timestamp']
        elif event['event'] == 'TIME':
            formatted_time = event['value']

    return jsonify({
        "start": start_time,
        "stop": stop_time,
        "formatted": formatted_time
    })

@app.route('/simulate_button_press', methods=['POST'])
def simulate_button_press():
    try:
        relay.start_unit.write(b"GO\n")
        print("Simulated button press sent to Arduino.")
        return jsonify({"status": "success", "message": "Button press simulated"}), 200
    except Exception as e:
        print(f"Error sending button press: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/")
def home():
    return render_template_string("""
    <!doctype html>
    <html>
      <head>
        <title>Run Robot Run Timer</title>
         <style>
          body {
            font-family: sans-serif;
            text-align: center;
            margin-top: 100px;
            background-color: #f4f7fc;
          }

          h1 {
            font-size: 2rem;
            color: #333;
          }

          #timer {
            font-size: 3rem;
            margin-top: 20px;
            color: #444;
          }

          #status {
            font-size: 1.25rem;
            color: #555;
            margin-top: 10px;
          }

          /* Button Styles */
          #simulatedButton {
            font-size: 1.2rem;
            padding: 12px 25px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s, transform 0.2s;
          }

          #simulatedButton:hover {
            background-color: #45a049;
            transform: scale(1.05);
          }

          #simulatedButton:active {
            background-color: #388e3c;
            transform: scale(0.98);
          }
        </style>
      </head>
      <body>
        <h1>Run Robot Run</h1>
        <div id="status">Waiting for signal...</div>
        <div id="timer">0:00:000</div>
        <button id="simulatedButton">Ready</button>
        <script>
          let start = null, stop = null, interval = null;

          document.getElementById('simulatedButton').addEventListener('click', async () => {
            try {
              await fetch('/simulate_button_press', {
                method: 'POST'
              });
            } catch (err) {
              console.error('Error pressing simulated button:', err);
            }
          });


          function formatTime(ms) {
            let min = Math.floor(ms / 60000),
                sec = Math.floor((ms % 60000) / 1000),
                msLeft = ms % 1000;
            return `${String(min).padStart(1, '0')}:${String(sec).padStart(2, '0')}:${String(msLeft).padStart(3, '0')}`;
          }

          async function fetchTimerData() {
            try {
              const res = await fetch('/timer');
              const data = await res.json();


              const { start: s, stop: e, formatted } = data;

              if (s !== null && e === null) {
                if (start !== s) {
                  start = s;
                  stop = null;
                  document.getElementById('status').innerText = "Timer running...";
                  if (interval) clearInterval(interval);
                  interval = setInterval(() => {
                    const elapsed = Date.now() - start;
                    document.getElementById('timer').innerText = formatTime(elapsed);
                  }, 50);
                }
              }

              if (s !== null && e !== null) {
                if (stop !== e || document.getElementById('timer').innerText !== formatted) {
                  stop = e;
                  clearInterval(interval);
                  document.getElementById('status').innerText = "Final recorded time:";
                  document.getElementById('timer').innerText = formatted;
                }
              }
            } catch (err) {
              console.error('Fetch error:', err);
            }
          }

          setInterval(fetchTimerData, 300);
          window.onload = fetchTimerData;
        </script>
      </body>
    </html>
    """)

if __name__ == "__main__":
    threading.Thread(target=relay.start_relay, daemon=True).start()
    app.run(port=5000)
