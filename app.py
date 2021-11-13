from server import app
import os
if __name__ == '__main__':
    port = int(8000)
    app.run(host='0.0.0.0', port=port, debug=True)