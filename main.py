import tempfile
import os
from flask import Flask, request, redirect, send_file
from skimage import io
import base64
import glob
import numpy as np

app = Flask(__name__)

main_html = """
<html>
<head>
<style>
  .color-btn {
    width: 40px;
    height: 40px;
    margin: 5px;
    border: 2px solid #333;
    cursor: pointer;
    display: inline-block;
  }
  .color-btn.selected {
    border: 3px solid #000;
    box-shadow: 0 0 5px rgba(0,0,0,0.5);
  }
</style>
</head>
<script>
  var mousePressed = false;
  var lastX, lastY;
  var ctx;
  var currentColor = '#FF0000'; // Default red

   function getRndInteger(min, max) {
    return Math.floor(Math.random() * (max - min) ) + min;
   }

   function selectColor(color, element) {
    currentColor = color;
    // Remove selected class from all buttons
    var buttons = document.getElementsByClassName('color-btn');
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].classList.remove('selected');
    }
    // Add selected class to clicked button
    element.classList.add('selected');
   }

  function InitThis() {
      ctx = document.getElementById('myCanvas').getContext("2d");


      numero = getRndInteger(0, 10);
      frutas = ["manzana", "platano", "naranja", "sandia", "pina", "uva"];
      etiquetas = ["Manzana", "Plátano", "Naranja", "Sandía", "Piña", "Uva"]
      random = Math.floor(Math.random() * frutas.length);
      aleatorio = frutas[random];

      document.getElementById('mensaje').innerHTML  = 'Dibujando una fruta: ' + etiquetas[random];
      document.getElementById('numero').value = aleatorio;

      $('#myCanvas').mousedown(function (e) {
          mousePressed = true;
          Draw(e.pageX - $(this).offset().left, e.pageY - $(this).offset().top, false);
      });

      $('#myCanvas').mousemove(function (e) {
          if (mousePressed) {
              Draw(e.pageX - $(this).offset().left, e.pageY - $(this).offset().top, true);
          }
      });

      $('#myCanvas').mouseup(function (e) {
          mousePressed = false;
      });
  	    $('#myCanvas').mouseleave(function (e) {
          mousePressed = false;
      });
  }

  function Draw(x, y, isDown) {
      if (isDown) {
          ctx.beginPath();
          ctx.strokeStyle = currentColor;
          ctx.lineWidth = 11;
          ctx.lineJoin = "round";
          ctx.moveTo(lastX, lastY);
          ctx.lineTo(x, y);
          ctx.closePath();
          ctx.stroke();
      }
      lastX = x; lastY = y;
  }

  function clearArea() {
      // Use the identity matrix while clearing the canvas
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  }

  //https://www.askingbox.com/tutorial/send-html5-canvas-as-image-to-server
  function prepareImg() {
     var canvas = document.getElementById('myCanvas');
     document.getElementById('myImage').value = canvas.toDataURL();
  }



</script>
<body onload="InitThis();">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>
    <script type="text/javascript" ></script>
    <div align="left">
      <img src="https://upload.wikimedia.org/wikipedia/commons/f/f7/Uni-logo_transparente_granate.png" width="300"/>
    </div>
    <div align="center">
        <h1 id="mensaje">Dibujando...</h1>
        <canvas id="myCanvas" width="200" height="200" style="border:2px solid black"></canvas>
        <br/>
        <br/>
        <div style="margin: 10px;">
          <strong>Colores:</strong><br/>
          <div class="color-btn selected" style="background-color: #FF0000;" onclick="selectColor('#FF0000', this)" title="Rojo"></div>
          <div class="color-btn" style="background-color: #FFFF00;" onclick="selectColor('#FFFF00', this)" title="Amarillo"></div>
          <div class="color-btn" style="background-color: #FFA500;" onclick="selectColor('#FFA500', this)" title="Naranja"></div>
          <div class="color-btn" style="background-color: #00FF00;" onclick="selectColor('#00FF00', this)" title="Verde"></div>
          <div class="color-btn" style="background-color: #8B4513;" onclick="selectColor('#8B4513', this)" title="Marrón"></div>
          <div class="color-btn" style="background-color: #800080;" onclick="selectColor('#800080', this)" title="Morado"></div>
          <div class="color-btn" style="background-color: #FFC0CB;" onclick="selectColor('#FFC0CB', this)" title="Rosa"></div>
        </div>
        <br/>
        <button onclick="javascript:clearArea();return false;">Borrar</button>
    </div>
    <div align="center">
      <form method="post" action="upload" onsubmit="javascript:prepareImg();"  enctype="multipart/form-data">
      <input id="numero" name="numero" type="hidden" value="">
      <input id="myImage" name="myImage" type="hidden" value="">
      <input id="bt_upload" type="submit" value="Enviar">
      </form>
    </div>
</body>
</html>

"""

@app.route("/")
def main():
    return(main_html)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # check if the post request has the file part
        img_data = request.form.get('myImage').replace("data:image/png;base64,","")
        aleatorio = request.form.get('numero')
        print(aleatorio)
        with tempfile.NamedTemporaryFile(delete = False, mode = "w+b", suffix='.png', dir=str(aleatorio)) as fh:
            fh.write(base64.b64decode(img_data))
        #file = request.files['myImage']
        print("Image uploaded")
    except Exception as err:
        print("Error occurred")
        print(err)

    return redirect("/", code=302)


@app.route('/status', methods=['GET'])
def status():
    fruits = ['manzana', 'platano', 'naranja', 'sandia', 'pina', 'uva']
    status_info = "<h2>System Status</h2>"
    total_images = 0

    for fruit in fruits:
        if os.path.exists(fruit):
            count = len(glob.glob('{}/*.png'.format(fruit)))
            total_images += count
            status_info += "<p>{}: {} images</p>".format(fruit, count)
        else:
            status_info += "<p>{}: directory not found</p>".format(fruit)

    status_info += "<p><strong>Total: {} images</strong></p>".format(total_images)
    status_info += "<p>X.npy exists: {}</p>".format(os.path.exists('X.npy'))
    status_info += "<p>y.npy exists: {}</p>".format(os.path.exists('y.npy'))

    return status_info

@app.route('/prepare', methods=['GET'])
def prepare_dataset():
    try:
        images = []
        fruits = ['manzana', 'platano', 'naranja', 'sandia', 'pina', 'uva']
        labels = []
        for fruit in fruits:
          filelist = glob.glob('{}/*.png'.format(fruit))
          if len(filelist) > 0:
            images_read = io.concatenate_images(io.imread_collection(filelist))
            images_read = images_read[:, :, :, 3]
            labels_read = np.array([fruit] * images_read.shape[0])
            images.append(images_read)
            labels.append(labels_read)

        if len(images) == 0:
            return "Error: No images found. Please upload some drawings first.", 400

        images = np.vstack(images)
        labels = np.concatenate(labels)
        np.save('X.npy', images)
        np.save('y.npy', labels)
        return "OK! Dataset prepared with {} images.".format(len(labels))
    except Exception as e:
        return "Error preparing dataset: {}".format(str(e)), 500

@app.route('/X.npy', methods=['GET'])
def download_X():
    if not os.path.exists('X.npy'):
        return "Error: X.npy not found. Please run /prepare first to generate the dataset.", 404
    return send_file('./X.npy')

@app.route('/y.npy', methods=['GET'])
def download_y():
    if not os.path.exists('y.npy'):
        return "Error: y.npy not found. Please run /prepare first to generate the dataset.", 404
    return send_file('./y.npy')

if __name__ == "__main__":
    fruits = ['manzana', 'platano', 'naranja', 'sandia', 'pina', 'uva']
    for fruit in fruits:
        if not os.path.exists(str(fruit)):
            os.mkdir(str(fruit))
    app.run()
