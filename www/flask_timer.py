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

@app.route("/connection_status")
def get_connection_status():
    start_connected = relay.start_unit is not None and relay.start_unit.is_open
    finish_connected = relay.finish_unit is not None and relay.finish_unit.is_open
    return jsonify({
        "start_connected": start_connected,
        "finish_connected": finish_connected
    })

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
        elif event['event'] == 'WAITING':
            return jsonify({
                "start": start_time,
                "stop": stop_time,
                "formatted": formatted_time,
                "status": "Waiting for player..."
            })

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

@app.route('/stop_timer', methods=['POST'])
def stop_timer():
    try:
        relay.finish_unit.write(b"STOPPED\n")
        print("Timer has been stopped.")
        return jsonify({"status": "success", "message": "Timer stopped successfully"}), 200
    except Exception as e:
        print(f"Error stopping timer: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/reset_timer', methods=['POST'])
def reset_timer():
    global start_time, stop_time, formatted_time
    try:
        if start_time is not None and stop_time is None:
            return jsonify({"status": "error", "message": "Timer is still running, cannot reset."}), 400
        else:
            start_time = None
            stop_time = None
            formatted_time = "0:00:000"
            print("Timer has been reset.")
            return jsonify({"status": "success", "message": "Timer reset successful"}), 200
    except Exception as e:
        print(f"Error resetting timer: {e}")
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

          #connection-status {
            font-size: 1rem;
            color: #666;
            margin-top: 10px;
          }

          .connection-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
          }

          .connected {
            background-color: #4CAF50;
          }

          .disconnected {
            background-color: #f44336;
          }

          /* Button Styles */
          #simulatedButton, #stopButton, #resetButton {
            font-size: 1.2rem;
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s, transform 0.2s;
            margin: 5px;  /* Adjust margin to space buttons evenly */
          }

          #simulatedButton {
            background-color: #4CAF50;
            color: white;
          }

          #simulatedButton:hover {
            background-color: #45a049;
            transform: scale(1.05);
          }

          #simulatedButton:active {
            background-color: #388e3c;
            transform: scale(0.98);
          }

          #stopButton {
            background-color: #ff9800;
            color: white;
          }

          #stopButton:hover {
            background-color: #f57c00;
            transform: scale(1.05);
          }

          #stopButton:active {
            background-color: #ef6c00;
            transform: scale(0.98);
          }

          #resetButton {
            background-color: #f44336;
            color: white;
          }

          #resetButton:hover {
            background-color: #e53935;
            transform: scale(1.05);
          }

          #resetButton:active {
            background-color: #c62828;
            transform: scale(0.98);
          }

          .button-container {
            display: flex;
            justify-content: center; /* Center buttons horizontally */
            gap: 10px;  /* Space between buttons */
            margin-top: 20px;
          }
        </style>
      </head>
      <body>
        <h1>Run Robot Run</h1>
        <div id="connection-status">
          Start Unit: <span class="connection-indicator disconnected" id="start-indicator"></span>
          Finish Unit: <span class="connection-indicator disconnected" id="finish-indicator"></span>
        </div>
        <div id="status">Waiting for signal...</div>
        <div id="timer">0:00:000</div>
        <div class="button-container">
          <button id="simulatedButton">Ready</button>
          <button id="stopButton">Stop</button>
          <button id="resetButton">Reset</button>
        </div>
        <script>
          let start = null, stop = null, interval = null, isRunning = false;

          document.getElementById('simulatedButton').addEventListener('click', async () => {
            try {
              await fetch('/simulate_button_press', {
                method: 'POST'
              });
              document.getElementById('status').innerText = "Waiting for player...";
            } catch (err) {
              console.error('Error pressing simulated button:', err);
            }
          });

          document.getElementById('stopButton').addEventListener('click', async () => {
            try {
              await fetch('/stop_timer', {
                method: 'POST'
              });
              if (isRunning) {
                isRunning = false;
                if (interval) clearInterval(interval);
                document.getElementById('status').innerText = "Timer stopped";
              }
            } catch (err) {
              console.error('Error stopping timer:', err);
            }
          });

          document.getElementById('resetButton').addEventListener('click', async () => {
            try {
              await fetch('/reset_timer', {
                method: 'POST'
              });
              start = null;
              stop = null;
              isRunning = false;
              if (interval) clearInterval(interval);
              document.getElementById('status').innerText = "Waiting for signal...";
              document.getElementById('timer').innerText = "0:00:000";
            } catch (err) {
              console.error('Error resetting timer:', err);
            }
          });

          function formatTime(ms) {
            let min = Math.floor(ms / 60000),
                sec = Math.floor((ms % 60000) / 1000),
                msLeft = ms % 1000;
            return `${min}:${String(sec).padStart(2, '0')}:${String(msLeft).padStart(3, '0')}`;
          }

          async function fetchTimerData() {
            try {
              const res = await fetch('/timer');
              const data = await res.json();

              const { start: s, stop: e, formatted, status } = data;

              if (status) {
                document.getElementById('status').innerText = status;
              }

              if (s !== null && e === null) {
                if (start !== s) {
                  start = s;
                  stop = null;
                  isRunning = true;
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
                  isRunning = false;
                  clearInterval(interval);
                  document.getElementById('status').innerText = "Final recorded time:";
                  document.getElementById('timer').innerText = formatted;
                }
              }
            } catch (err) {
              console.error('Fetch error:', err);
            }
          }

          async function checkConnectionStatus() {
            try {
              const res = await fetch('/connection_status');
              const data = await res.json();

              const startIndicator = document.getElementById('start-indicator');
              const finishIndicator = document.getElementById('finish-indicator');

              startIndicator.className = `connection-indicator ${data.start_connected ? 'connected' : 'disconnected'}`;
              finishIndicator.className = `connection-indicator ${data.finish_connected ? 'connected' : 'disconnected'}`;

              if (!data.start_connected || !data.finish_connected) {
                document.getElementById('status').innerText = "Waiting for Bluetooth connection...";
              } else if (document.getElementById('status').innerText === "Waiting for Bluetooth connection...") {
                document.getElementById('status').innerText = "Waiting for signal...";
              }
            } catch (err) {
              console.error('Connection status check error:', err);
            }
          }

          setInterval(checkConnectionStatus, 1000);
          setInterval(fetchTimerData, 300);
          window.onload = () => {
            fetchTimerData();
            checkConnectionStatus();
          };
        </script>
      </body>
    </html>
    """)

if __name__ == "__main__":
    threading.Thread(target=relay.start_relay, daemon=True).start()
    app.run(port=5000)
