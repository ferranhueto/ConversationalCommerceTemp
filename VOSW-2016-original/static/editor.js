/**
 * Created by ferranhueto on 08/08/16.
 */
var canvas = document.getElementById('canvas');
var context= canvas.getContext('2d');
context.lineWidth = 5;
var down = false;
var type = "pen";
var initCoorX;
var initCoorY;


canvas.addEventListener('mousemove', draw);

canvas.addEventListener('mousedown', function()
{
    if (type == "pen") {
        down = true;
        context.beginPath();
        context.moveTo(xPos, yPos);
        canvas.addEventListener("mousemove", draw);
    }
    else if (type == "square") {
        down = true;
        context.beginPath();
        initCoorX = xPos;
        initCoorY = yPos;
    }
    
});

canvas.addEventListener('mouseup', function() { 
    down = false;
    
    if (type == "square") {
        var x = xPos - initCoorX;
        var y = yPos - initCoorY;
        context.rect(initCoorX,initCoorY,x,y);
        context.fill();
    }
                                              
});

function draw(e)
{
    xPos = e.pageX - canvas.offsetLeft;
    yPos = e.pageY - canvas.offsetTop;
    
    if (down == true && type == "pen")
        {
            context.lineTo(xPos, yPos);
            context.stroke();
        }
    
}

function changeColor(color) { 
    context.strokeStyle = color; 
    context.fillStyle = color; 
}

function clearCanvas() {
    context.clearRect(0, 0, canvas.width, canvas.height);
}

function erase() { 
    type = "pen";
    context.strokeStyle = "white"; 
    context.lineWidth = 20; 
}

function pen() {
    type = "pen";
    context.strokeStyle = "black"; 
    context.lineWidth = 5; 
}

function square() { type = "square" }

function something() {
    a = document.getElementById('text').value;
    context.font = "14px Arial";
    context.fillText(a, 20, 20);
    document.getElementById('text').value = '';


}
function saveCards()
{
    var data = canvas.toDataURL();
    
    $.ajax({
        type: "POST",
        url: "/save",
        data: JSON.stringify({title: data}),
        contentType: 'application/json;charset=UTF-8',
        success: function() {
        alert('Good'); },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
        alert("Error: " + errorThrown); }
}).done(function(o) {
  console.log('saved');
});

}